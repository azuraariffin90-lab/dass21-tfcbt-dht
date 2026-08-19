from __future__ import annotations

import hmac
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from scoring import calculate_dass, calculate_trauma, determine_review_priority
from storage import append_submission, initialize_database, read_database, read_database_bytes
from survey_config import (
    APP_VERSION,
    ASSESSMENT_PHASES,
    DASS_ITEMS,
    DASS_OPTIONS,
    DASS_SCORING_REFERENCE,
    DHT_REFERENCE,
    KKM_DASS_URL,
    SEVERITY_ORDER,
    TF_CBT_REFERENCE,
    TRAUMA_ITEMS,
    TRAUMA_OPTIONS,
)


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "database_template.xlsx"
DATABASE_PATH = Path(
    os.getenv("DASS_DATABASE_PATH", str(BASE_DIR / "data" / "dass_tfcbt_dht_database.xlsx"))
).expanduser()


st.set_page_config(
    page_title="Saringan DASS-21 | TF-CBT-DHT",
    page_icon="🫶",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      :root { --ink:#18332f; --teal:#0f766e; --mint:#e8f5f1; --amber:#f6c453; }
      .stApp { background: linear-gradient(180deg,#f7fbfa 0,#ffffff 24rem); }
      [data-testid="stSidebar"] { background:#102f2c; }
      [data-testid="stSidebar"] * { color:#f5fffc; }
      h1,h2,h3 { color:var(--ink); letter-spacing:-.02em; }
      .hero { padding:1.25rem 1.4rem; border-radius:18px; color:#fff;
              background:linear-gradient(120deg,#0f766e,#174f55); margin-bottom:1rem; }
      .hero h1,.hero p { color:#fff; margin:.1rem 0; }
      .soft-card { border:1px solid #dcebe7; border-radius:14px; padding:1rem 1.1rem;
                   background:rgba(255,255,255,.88); margin:.45rem 0 1rem; }
      .source-note { font-size:.88rem; color:#4d6661; }
      .privacy-pill { display:inline-block; padding:.3rem .65rem; border-radius:999px;
                      background:#e2f3ee; color:#155e55; font-weight:650; margin:.15rem; }
      div[data-testid="stMetric"] { border:1px solid #dcebe7; border-radius:14px;
                                    background:white; padding:.65rem 1rem; }
      .urgent { border-left:5px solid #c2410c; padding:.8rem 1rem; background:#fff5ed; }
      footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _admin_password() -> str | None:
    password = os.getenv("DASS_ADMIN_PASSWORD")
    if password:
        return password
    try:
        return st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        return None


def _display_hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <h1>Saringan Kesejahteraan Pelajar</h1>
          <p>DASS-21 dan indikator eksploratori TF-CBT-DHT untuk kegunaan penyelidikan setempat.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _result_cards(result: dict) -> None:
    columns = st.columns(3)
    labels = {"Depression": "Kemurungan", "Anxiety": "Kebimbangan", "Stress": "Stres"}
    for column, scale in zip(columns, ("Depression", "Anxiety", "Stress")):
        column.metric(labels[scale], result["scores"][scale], result["levels"][scale])


def _student_form() -> None:
    _display_hero()
    st.info(
        "Ini ialah saringan kendiri dan alat pengumpulan data penyelidikan, bukan diagnosis. "
        "Jawab berdasarkan keadaan sepanjang minggu yang lalu untuk bahagian DASS-21."
    )

    with st.form("student_assessment", clear_on_submit=False):
        st.subheader("1 · Maklumat penyelidikan minimum")
        col_a, col_b, col_c = st.columns(3)
        student_id = col_a.text_input(
            "ID pelajar / kod peserta *",
            placeholder="Contoh: P2026-014",
            help="Gunakan kod kajian; jangan masukkan nama atau nombor kad pengenalan.",
        ).strip()
        cohort = col_b.text_input("Kohort / kelas", placeholder="Contoh: Kohort A").strip()
        assessment_phase = col_c.selectbox("Fasa penilaian", ASSESSMENT_PHASES)
        consent_dass = st.checkbox(
            "Saya memahami tujuan saringan dan bersetuju menghantar jawapan DASS-21 untuk tujuan yang diterangkan. *"
        )

        st.divider()
        st.subheader("2 · DASS-21")
        st.caption(
            "0 = tidak langsung · 1 = sedikit/jarang · 2 = banyak/kerap · 3 = sangat banyak/sangat kerap"
        )
        dass_answers: dict[int, int | None] = {}
        for item in DASS_ITEMS:
            dass_answers[item["id"]] = st.radio(
                f"{item['id']}. {item['text']}",
                options=list(DASS_OPTIONS),
                format_func=lambda value: f"{value} — {DASS_OPTIONS[value]}",
                index=None,
                key=f"dass_{item['id']}",
            )

        st.divider()
        st.subheader("3 · Saringan trauma TF-CBT-DHT (pilihan)")
        st.warning(
            "15 item berikut ialah indikator eksploratori kajian, bukan instrumen trauma/PTSD yang telah divalidasi. "
            "Anda boleh tidak menyertai bahagian ini tanpa menjejaskan submission DASS-21."
        )
        consent_trauma = st.checkbox(
            "Saya bersetuju menjawab item trauma pilihan ini untuk tujuan penyelidikan."
        )
        trauma_answers: dict[str, int | None] = {item["id"]: None for item in TRAUMA_ITEMS}
        if consent_trauma:
            st.caption(
                "Rujuk pengalaman sepanjang 4 minggu yang lalu, kecuali item yang menyebut ‘pada masa ini’. "
                "Biarkan item kosong jika tidak berkaitan atau anda memilih untuk tidak menjawab."
            )
            for item in TRAUMA_ITEMS:
                trauma_answers[item["id"]] = st.radio(
                    f"{item['id']} · {item['text']}",
                    options=list(TRAUMA_OPTIONS),
                    format_func=lambda value: f"{value} — {TRAUMA_OPTIONS[value]}",
                    index=None,
                    key=f"trauma_{item['id']}",
                )

        submitted = st.form_submit_button("Hantar saringan", type="primary", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{2,31}", student_id):
        validation_errors.append(
            "ID pelajar perlu 3–32 aksara dan hanya boleh mengandungi huruf, nombor, tanda sempang atau garis bawah."
        )
    if not consent_dass:
        validation_errors.append("Persetujuan DASS-21 diperlukan sebelum submission.")
    missing_dass = [str(item_id) for item_id, value in dass_answers.items() if value is None]
    if missing_dass:
        validation_errors.append("Jawab semua item DASS-21. Item belum dijawab: " + ", ".join(missing_dass))
    if validation_errors:
        for message in validation_errors:
            st.error(message)
        return

    clean_dass = {item_id: int(value) for item_id, value in dass_answers.items() if value is not None}
    dass_result = calculate_dass(clean_dass)
    trauma_result = calculate_trauma(trauma_answers)
    priority = determine_review_priority(dass_result, trauma_result)
    submission_id = str(uuid.uuid4())
    submitted_at = datetime.now(ZoneInfo("Asia/Kuala_Lumpur")).isoformat(timespec="seconds")

    record = {
        "submission_id": submission_id,
        "submitted_at": submitted_at,
        "student_id": student_id.upper(),
        "cohort": cohort,
        "assessment_phase": assessment_phase,
        "consent_dass": "Ya",
        "consent_trauma": "Ya" if consent_trauma else "Tidak",
        **{f"dass_q{item_id:02d}": value for item_id, value in clean_dass.items()},
        "depression_raw": dass_result["raw"]["Depression"],
        "anxiety_raw": dass_result["raw"]["Anxiety"],
        "stress_raw": dass_result["raw"]["Stress"],
        "depression_score": dass_result["scores"]["Depression"],
        "anxiety_score": dass_result["scores"]["Anxiety"],
        "stress_score": dass_result["scores"]["Stress"],
        "depression_level": dass_result["levels"]["Depression"],
        "anxiety_level": dass_result["levels"]["Anxiety"],
        "stress_level": dass_result["levels"]["Stress"],
        "highest_dass_level": dass_result["highest_level"],
        "trauma_answered_count": trauma_result["answered_count"],
        "trauma_positive_count": trauma_result["positive_count"],
        "trauma_dharuriyyat_positive_count": trauma_result["dharuriyyat_positive_count"],
        "immediate_safety_flag": "Ya" if trauma_result["immediate_safety_flag"] else "Tidak",
        "review_priority": priority,
        "trauma_domains_flagged": ", ".join(trauma_result["domains_flagged"]),
        "trauma_items_flagged": ", ".join(trauma_result["positive_items"]),
        **{f"trauma_{item['id'].lower()}": trauma_answers[item["id"]] for item in TRAUMA_ITEMS},
        "app_version": APP_VERSION,
    }

    trauma_rows = []
    for item in TRAUMA_ITEMS:
        response = trauma_answers[item["id"]]
        if response is None:
            continue
        trauma_rows.append(
            {
                "submission_id": submission_id,
                "submitted_at": submitted_at,
                "student_id": student_id.upper(),
                "item_id": item["id"],
                "response": response,
                "positive_flag": "Ya" if response >= 2 else "Tidak",
                "dht_domain": item["domain"],
                "need_level": item["need_level"],
                "tfcbt_impact": item["tfcbt_impact"],
                "safety_critical": "Ya" if item["safety_critical"] else "Tidak",
                "item_text": item["text"],
            }
        )

    try:
        append_submission(DATABASE_PATH, record, trauma_rows)
    except PermissionError:
        st.error(
            "Pangkalan data Excel sedang dibuka atau dikunci. Tutup fail Excel tersebut dan cuba hantar semula."
        )
        return
    except Exception as exc:
        st.error(f"Submission tidak dapat disimpan: {exc}")
        return

    st.success(f"Submission berjaya disimpan. Kod rekod: {submission_id[:8]}")
    _result_cards(dass_result)
    st.caption("Skor dipaparkan untuk maklum balas saringan sahaja dan bukan diagnosis klinikal.")

    if trauma_result["immediate_safety_flag"]:
        st.markdown(
            """
            <div class="urgent"><strong>Utamakan keselamatan sekarang.</strong><br>
            Aplikasi ini tidak menghantar amaran automatik kepada pensyarah atau kaunselor.
            Hubungi 999 jika terdapat bahaya segera, atau Talian HEAL 15555 untuk sokongan kesihatan mental.
            Hubungi juga pegawai psikologi/kaunselor institusi yang dipercayai.</div>
            """,
            unsafe_allow_html=True,
        )
    elif dass_result["highest_level"] in ("Teruk", "Sangat Teruk"):
        st.warning(
            "Keputusan menunjukkan tahap yang wajar disemak dengan profesional. Pertimbangkan pegawai psikologi/kaunselor "
            "institusi atau Talian HEAL 15555. Jika ada bahaya segera, hubungi 999."
        )


def _admin_login() -> bool:
    configured = _admin_password()
    if not configured:
        st.error(
            "Dashboard admin dinyahaktifkan kerana kata laluan belum ditetapkan. "
            "Tetapkan pemboleh ubah DASS_ADMIN_PASSWORD sebelum memulakan aplikasi."
        )
        return False
    if st.session_state.get("admin_authenticated"):
        return True
    with st.form("admin_login"):
        entered = st.text_input("Kata laluan admin", type="password")
        login = st.form_submit_button("Log masuk", type="primary")
    if login:
        if hmac.compare_digest(entered, configured):
            st.session_state["admin_authenticated"] = True
            st.rerun()
        else:
            st.error("Kata laluan tidak tepat.")
    return False


def _admin_dashboard() -> None:
    _display_hero()
    st.subheader("Dashboard admin")
    st.caption("Akses setempat · data berpseudonim · tiada notifikasi kecemasan automatik")
    if not _admin_login():
        return

    top_left, top_right = st.columns([5, 1])
    top_left.success("Sesi admin aktif.")
    if top_right.button("Log keluar", use_container_width=True):
        st.session_state["admin_authenticated"] = False
        st.rerun()

    submissions, trauma = read_database(DATABASE_PATH)
    if submissions.empty:
        st.info("Belum ada submission dalam pangkalan data.")
        return

    submissions["submitted_at"] = pd.to_datetime(submissions["submitted_at"], errors="coerce")
    st.subheader("Penapis")
    f1, f2, f3, f4 = st.columns(4)
    student_search = f1.text_input("Cari ID pelajar")
    cohort_options = sorted(submissions["cohort"].dropna().astype(str).unique().tolist())
    cohorts = f2.multiselect("Kohort", cohort_options)
    phases = f3.multiselect(
        "Fasa penilaian", sorted(submissions["assessment_phase"].dropna().astype(str).unique())
    )
    priorities = f4.multiselect(
        "Keutamaan semakan", ["Segera", "Tinggi", "Sederhana", "Rutin"]
    )

    s1, s2, s3, s4 = st.columns(4)
    depression_levels = s1.multiselect("Tahap kemurungan", SEVERITY_ORDER)
    anxiety_levels = s2.multiselect("Tahap kebimbangan", SEVERITY_ORDER)
    stress_levels = s3.multiselect("Tahap stres", SEVERITY_ORDER)
    safety_only = s4.toggle("Bendera keselamatan sahaja")

    t1, t2, t3 = st.columns(3)
    domains = t1.multiselect("Domain DHT trauma", ["Agama", "Nyawa", "Akal", "Keturunan", "Harta"])
    item_options = [f"{item['id']} — {item['text']}" for item in TRAUMA_ITEMS]
    selected_item_labels = t2.multiselect("Item trauma", item_options)
    minimum_response = t3.slider("Respons trauma minimum", 0, 3, 2)
    selected_item_ids = [label.split(" — ", 1)[0] for label in selected_item_labels]

    filtered = submissions.copy()
    if student_search:
        filtered = filtered[
            filtered["student_id"].astype("string").str.contains(
                student_search, case=False, na=False, regex=False
            )
        ]
    if cohorts:
        filtered = filtered[filtered["cohort"].astype(str).isin(cohorts)]
    if phases:
        filtered = filtered[filtered["assessment_phase"].isin(phases)]
    if priorities:
        filtered = filtered[filtered["review_priority"].isin(priorities)]
    if depression_levels:
        filtered = filtered[filtered["depression_level"].isin(depression_levels)]
    if anxiety_levels:
        filtered = filtered[filtered["anxiety_level"].isin(anxiety_levels)]
    if stress_levels:
        filtered = filtered[filtered["stress_level"].isin(stress_levels)]
    if safety_only:
        filtered = filtered[filtered["immediate_safety_flag"] == "Ya"]

    if domains or selected_item_ids:
        trauma_match = trauma.copy()
        trauma_match["response"] = pd.to_numeric(trauma_match["response"], errors="coerce")
        trauma_match = trauma_match[trauma_match["response"] >= minimum_response]
        if domains:
            trauma_match = trauma_match[trauma_match["dht_domain"].isin(domains)]
        if selected_item_ids:
            trauma_match = trauma_match[trauma_match["item_id"].isin(selected_item_ids)]
        filtered = filtered[filtered["submission_id"].isin(trauma_match["submission_id"])]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rekod dipaparkan", len(filtered))
    m2.metric("Perlu semakan tinggi/segera", int(filtered["review_priority"].isin(["Tinggi", "Segera"]).sum()))
    m3.metric("Bendera keselamatan", int((filtered["immediate_safety_flag"] == "Ya").sum()))
    m4.metric("Ada indikator trauma ≥2", int((pd.to_numeric(filtered["trauma_positive_count"], errors="coerce") > 0).sum()))

    st.subheader("Senarai submission")
    display_columns = [
        "submitted_at",
        "student_id",
        "cohort",
        "assessment_phase",
        "depression_score",
        "depression_level",
        "anxiety_score",
        "anxiety_level",
        "stress_score",
        "stress_level",
        "review_priority",
        "immediate_safety_flag",
        "trauma_domains_flagged",
        "trauma_items_flagged",
    ]
    st.dataframe(
        filtered[display_columns].sort_values("submitted_at", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "submitted_at": st.column_config.DatetimeColumn("Tarikh/hora", format="DD/MM/YYYY HH:mm"),
            "student_id": "ID pelajar",
            "review_priority": "Keutamaan",
            "immediate_safety_flag": "Keselamatan",
        },
    )

    chart_left, chart_right = st.columns(2)
    with chart_left:
        st.caption("Taburan tahap tertinggi DASS")
        severity_counts = (
            filtered["highest_dass_level"].value_counts().reindex(SEVERITY_ORDER, fill_value=0)
        )
        st.bar_chart(severity_counts, color="#0f766e")
    with chart_right:
        st.caption("Domain DHT yang ditanda (respons ≥2)")
        if not trauma.empty and not filtered.empty:
            relevant_trauma = trauma[
                trauma["submission_id"].isin(filtered["submission_id"])
                & (pd.to_numeric(trauma["response"], errors="coerce") >= 2)
            ]
            domain_counts = relevant_trauma["dht_domain"].value_counts()
            st.bar_chart(domain_counts, color="#d97706")
        else:
            st.caption("Tiada data trauma untuk rekod dipaparkan.")

    st.subheader("Muat turun")
    d1, d2 = st.columns(2)
    d1.download_button(
        "CSV rekod ditapis",
        data=filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="submission_ditapis.csv",
        mime="text/csv",
        use_container_width=True,
    )
    d2.download_button(
        "Pangkalan data Excel penuh",
        data=read_database_bytes(DATABASE_PATH),
        file_name=DATABASE_PATH.name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    st.warning(
        "Simpan eksport dalam lokasi terhad akses. Jangan e-melkan fail mentah tanpa perlindungan, "
        "dan elakkan menggabungkan ID kajian dengan senarai nama dalam folder yang sama."
    )


def _about() -> None:
    _display_hero()
    st.subheader("Skop, kaedah dan batasan")
    st.markdown(
        f"""
        - **DASS-21:** 21 item, 7 item bagi setiap subskala. Jumlah mentah setiap subskala didarab 2,
          kemudian dipadankan kepada tahap Normal, Ringan, Sederhana, Teruk atau Sangat Teruk.
        - **Trauma TF-CBT-DHT:** 15 indikator eksploratori merentas Agama, Nyawa, Akal, Keturunan dan Harta,
          serta Dharuriyyat, Hajiyyat dan Tahsiniyyat. Respons ≥2 ditanda untuk analisis; TR01/TR07 mencetuskan
          bendera keselamatan apabila respons sekurang-kurangnya 1.
        - **Keutamaan semakan:** peraturan operasi prototaip, bukan triage klinikal dan bukan pengganti penilaian profesional.
        - **Tiada notifikasi automatik:** penyelidik perlu menyediakan SOP semakan, rujukan dan respons kecemasan sebelum kajian sebenar.

        Sumber: [Borang DASS awam KKM]({KKM_DASS_URL}) ·
        [pemarkahan DASS-21 dalam kajian Malaysia]({DASS_SCORING_REFERENCE}) ·
        [aplikasi DHT dalam kaunseling]({DHT_REFERENCE}) ·
        [domain impak TF-CBT]({TF_CBT_REFERENCE})
        """
    )
    st.subheader("Sebelum digunakan dalam kajian sebenar")
    st.markdown(
        """
        1. Dapatkan kelulusan Jawatankuasa Etika Penyelidikan dan persetujuan termaklum yang sesuai.
        2. Semak hak penggunaan/versi bahasa instrumen dan sahkan teks serta pemarkahan dengan pakar.
        3. Jalankan kesahan kandungan, kajian rintis dan analisis kebolehpercayaan untuk item trauma baharu.
        4. Tetapkan siapa menyemak bendera, berapa cepat semakan dibuat, dan laluan rujukan kecemasan.
        5. Simpan jadual pemadanan ID-kepada-nama secara berasingan, terenkripsi dan dengan akses minimum.
        """
    )
    st.info("Untuk bantuan kesihatan mental di Malaysia: Talian HEAL 15555. Jika ada bahaya segera, hubungi 999.")


def main() -> None:
    try:
        initialize_database(DATABASE_PATH, TEMPLATE_PATH)
    except Exception as exc:
        st.error(f"Pangkalan data tidak dapat disediakan: {exc}")
        st.stop()

    st.sidebar.title("TF-CBT · DHT")
    st.sidebar.caption("Prototaip penyelidikan setempat")
    page = st.sidebar.radio("Navigasi", ["Borang Pelajar", "Dashboard Admin", "Tentang & Etika"])
    st.sidebar.divider()
    st.sidebar.caption(f"Versi {APP_VERSION}")
    st.sidebar.caption("Data disimpan dalam fail Excel tempatan.")

    if page == "Borang Pelajar":
        _student_form()
    elif page == "Dashboard Admin":
        _admin_dashboard()
    else:
        _about()


if __name__ == "__main__":
    main()

