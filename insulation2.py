# insulation_estimator_app.py

import streamlit as st
import math
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Material specifications (coverage per bag and pieces per bag)
MATERIAL_SPECS = {
    'R12': {
        'widths': {
            15: {'coverage_per_bag': 100.0, 'pieces_per_bag': 20},
            23: {'coverage_per_bag': 153.3, 'pieces_per_bag': 20}
        }
    },
    'R14': {
        'widths': {
            15: {'coverage_per_bag': 78.3, 'pieces_per_bag': 16},
            23: {'coverage_per_bag': 120.1, 'pieces_per_bag': 16}
        }
    },
    'R20': {
        'widths': {
            15: {'coverage_per_bag': 80.0, 'pieces_per_bag': 16},
            23: {'coverage_per_bag': 122.7, 'pieces_per_bag': 16}
        }
    },
    'R22': {
        'widths': {
            15: {'coverage_per_bag': 49.0, 'pieces_per_bag': 10},
            23: {'coverage_per_bag': 75.1, 'pieces_per_bag': 10}
        }
    },
    'R28': {
        'widths': {
            16: {'coverage_per_bag': 53.3, 'pieces_per_bag': 10},
            24: {'coverage_per_bag': 80.0, 'pieces_per_bag': 10}
        }
    },
    'R31': {
        'widths': {
            16: {'coverage_per_bag': 42.7, 'pieces_per_bag': 8},
            24: {'coverage_per_bag': 64.0, 'pieces_per_bag': 8}
        }
    },
    'R40': {
        'widths': {
            16: {'coverage_per_bag': 32.0, 'pieces_per_bag': 6},
            24: {'coverage_per_bag': 48.0, 'pieces_per_bag': 6}
        }
    }
}

def save_pdf(text, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    y = 750
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Insulation Estimator Report")
    y -= 30
    c.setFont("Helvetica", 12)
    for line in text.split('\n'):
        c.drawString(50, y, line)
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.save()

def draw_cost_breakdown_chart(costs):
    labels = list(costs.keys())
    values = list(costs.values())
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title("Cost Breakdown")
    ax.set_ylabel("Cost ($)")
    ax.set_xticklabels(labels, rotation=45, ha='right')
    st.pyplot(fig)

def draw_cathedral_diagram(base_width, rise):
    x = [0, base_width/2, base_width]
    y = [0, rise, 0]
    fig, ax = plt.subplots()
    ax.plot(x, y, linewidth=2)
    ax.set_xlim(0, base_width)
    ax.set_ylim(0, rise)
    ax.set_title("Cathedral Ceiling Cross-Section")
    ax.set_xlabel("Width (ft)")
    ax.set_ylabel("Height Above Wall (ft)")
    ax.grid(True)
    fig.tight_layout()
    st.pyplot(fig)

# Streamlit config
st.set_page_config(page_title="Insulation Estimator", layout="wide")
st.title("Insulation Estimator")

tabs = st.tabs([
    "1. Materials",
    "2. Dimensions",
    "3. Labour & Surcharges",
    "4. Review & Download"
])

with tabs[0]:
    st.header("1. Materials")
    wall_r_value = st.selectbox("Wall Insulation R-value", list(MATERIAL_SPECS.keys()))
    wall_width = st.selectbox("Wall Insulation Width (inches)", list(MATERIAL_SPECS[wall_r_value]['widths']))
    wp = MATERIAL_SPECS[wall_r_value]['widths'][wall_width]
    st.write(f"Coverage: {wp['coverage_per_bag']} sqft/bag, Pieces: {wp['pieces_per_bag']} per bag")
    wall_price_per_bag = st.number_input("Wall Price per Bag ($)", min_value=0.0)

    cat_r_value = st.selectbox("Cathedral Insulation R-value", list(MATERIAL_SPECS.keys()))
    cat_width = st.selectbox("Cathedral Insulation Width (inches)", list(MATERIAL_SPECS[cat_r_value]['widths']))
    cp = MATERIAL_SPECS[cat_r_value]['widths'][cat_width]
    st.write(f"Coverage: {cp['coverage_per_bag']} sqft/bag, Pieces: {cp['pieces_per_bag']} per bag")
    cat_price_per_bag = st.number_input("Cathedral Price per Bag ($)", min_value=0.0)

    ceiling_cov_per_bag = st.number_input(
        "Blown-In Coverage per Bag (sqft/bag)",
        min_value=0.0,
        help="Sqft covered by one bag of blown-in insulation."
    )
    ceiling_price_per_bag = st.number_input(
        "Blown-In Price per Bag ($)",
        min_value=0.0,
        help="Cost per bag of blown-in insulation."
    )

with tabs[1]:
    st.header("2. Dimensions")
    st.subheader("Walls")
    wall_linear_feet = st.number_input("Wall Linear Feet (ft)", min_value=0.0)
    wall_height = st.number_input("Wall Height (ft)", min_value=0.0)
    wall_stud_spacing = st.selectbox("Wall Stud Spacing (inches)", [16, 24])

    st.subheader("Cathedral Sections")
    num_cat = st.number_input("Number of Cathedral Sections", min_value=1, step=1)
    cat_sections = []
    for i in range(int(num_cat)):
        st.markdown(f"**Section {i+1}**")
        length = st.number_input("Length (ft)", min_value=0.0, key=f"len_{i}")
        base_width = st.number_input("Base Width (ft)", min_value=0.0, key=f"wd_{i}")
        height_above = st.number_input("Height Above Wall (ft)", min_value=0.0, key=f"ht_{i}")
        cat_sections.append((length, base_width, height_above))

    st.subheader("Truss Spacing for Cathedrals")
    cat_spacing_in = st.selectbox("Spacing (inches)", [16, 24])

    st.subheader("Blown-In Ceiling")
    blow_sq = st.number_input("Blown-in Sq Ft", min_value=0)
    vault_sq = st.number_input("Vaulted/Cathedral Excl. Sq Ft", min_value=0)

with tabs[2]:
    st.header("3. Labour & Surcharges")
    wall_labour_rate = st.number_input("Wall Labour Rate per sqft ($)", min_value=0.0)
    ceiling_hourly = st.number_input("Ceiling Labour Rate per hour ($)", min_value=0.0)
    ceiling_hours = st.number_input("Ceiling Labour Time (hours)", min_value=0.0)
    ceiling_flat_srchg = st.number_input("Ceiling Flat Surcharge ($)", min_value=0.0)
    cathedral_hourly = st.number_input("Cathedral Labour Rate per hour ($)", min_value=0.0)
    cathedral_hours = st.number_input("Cathedral Labour Time per section (hours)", min_value=0.0)
    cathedral_flat = st.number_input("Cathedral Flat Surcharge per section ($)", min_value=0.0)

with tabs[3]:
    st.header("4. Review & Download")
    if st.button("Run Estimate"):
        # Materials
        wall_area = wall_linear_feet * wall_height
        wb_cov = wp['coverage_per_bag']; wb_pcs = wp['pieces_per_bag']
        wall_bags = math.ceil(wall_area / wb_cov)
        wall_pieces = wall_bags * wb_pcs
        wall_cost = wall_bags * wall_price_per_bag

        # Cathedrals (slope-based)
        cs_cov = cp['coverage_per_bag']; cs_pcs = cp['pieces_per_bag']
        total_cat_area = 0.0
        for length, bw, rise in cat_sections:
            slope = math.sqrt((bw/2)**2 + rise**2)
            total_cat_area += 2 * slope * length
        buffered_cov = cs_cov * 1.10
        cat_bags = math.ceil(total_cat_area / buffered_cov)
        cat_pieces = cat_bags * cs_pcs
        cat_cost = cat_bags * cat_price_per_bag

        # Ceiling
        ceiling_area = max(blow_sq - vault_sq, 0)
        ceiling_bags = math.ceil(ceiling_area / ceiling_cov_per_bag) if ceiling_cov_per_bag else 0
        ceiling_mat_cost = ceiling_bags * ceiling_price_per_bag

        # Batt counts
        wall_batts = math.ceil(wall_linear_feet / (wall_stud_spacing / 12))
        cat_batts = [math.ceil(bw / (cat_spacing_in / 12)) for _, bw, _ in cat_sections]

        # Labour & surcharges
        wall_lab = wall_area * wall_labour_rate
        area_lab = (wall_area + total_cat_area) * wall_labour_rate
        ceil_lab = ceiling_hourly * ceiling_hours + ceiling_flat_srchg
        cat_surch = ((cathedral_hourly * cathedral_hours) + cathedral_flat) * int(num_cat)

        # Totals
        mat_total = wall_cost + cat_cost + ceiling_mat_cost
        lab_total = wall_lab + area_lab + ceil_lab + cat_surch
        total_tax = (mat_total + lab_total) * 1.05
        total_buf = total_tax * 1.10

        # Build summary text
        lines = [
            "Materials Summary:",
            f"  Wall:      {wall_area:.1f} sq ft → {wall_bags} bags ({wall_pieces} pcs) = ${wall_cost:.2f}",
            f"  Cathedral: {total_cat_area:.1f} sq ft → {cat_bags} bags ({cat_pieces} pcs) = ${cat_cost:.2f}",
            f"  Ceiling:   {ceiling_area:.1f} sq ft → {ceiling_bags} bags = ${ceiling_mat_cost:.2f}",
            "",
            "Labour & Surcharges:",
            f"  Wall Labour:                  ${wall_lab:.2f}",
            f"  Area Labour (Wall+Cathedral): ${area_lab:.2f}",
            f"  Ceiling Labour:               ${ceil_lab:.2f}",
            f"  Cathedral Surcharge:          ${cat_surch:.2f}",
            "",
            "Batt Counts:",
            f"  Wall batts: {wall_batts} pcs",
            f"  Cathedral batts: {sum(cat_batts)} pcs",
            "",
            "Totals:",
            f"  Material Total:       ${mat_total:.2f}",
            f"  Labour Total:         ${lab_total:.2f}",
            f"  Total w/ Tax:         ${total_tax:.2f}",
            f"  Total w/ Tax & Buffer:${total_buf:.2f}"
        ]
        summary_text = "\n".join(lines)

        # Display
        st.subheader("Materials Summary")
        st.write(lines[1]); st.write(lines[2]); st.write(lines[3])

        st.subheader("Labour & Surcharges")
        for l in lines[5:10]:
            st.write(l)

        st.subheader("Batt Counts")
        st.write(lines[12]); st.write(lines[13])

        st.subheader("Diagrams")
        for _, bw, rise in cat_sections:
            draw_cathedral_diagram(bw, rise)

        st.subheader("Totals")
        for l in lines[-4:]:
            st.write(l)

        st.subheader("Cost Breakdown Chart")
        costs = {
            'Wall Mat': wall_cost,
            'Cat Mat': cat_cost,
            'Ceil Mat': ceiling_mat_cost,
            'Wall Labour': wall_lab,
            'Area Labour': area_lab,
            'Ceil Labour': ceil_lab,
            'Cat Surcharge': cat_surch
        }
        draw_cost_breakdown_chart(costs)

        # PDF Export
        save_pdf(summary_text, "estimate_output.pdf")
        with open("estimate_output.pdf", "rb") as f:
            st.download_button("Download PDF", f, file_name="estimate_output.pdf")



