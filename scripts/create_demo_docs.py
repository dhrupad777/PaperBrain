"""
Generates synthetic demo documents for Paper Brain:
  data/docs/OEM-XR-900-Pump-Manual.pdf
  data/docs/Tribal-Bob-Notes.pdf

Run from repo root:  python scripts/create_demo_docs.py
"""

import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "docs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

NL = {"new_x": XPos.LMARGIN, "new_y": YPos.NEXT}   # replaces ln=True in fpdf2


W = 190  # usable page width in mm


def add_heading(pdf, text):
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 40, 80)
    pdf.set_x(10)
    pdf.cell(W, 9, text, **NL)
    pdf.set_draw_color(20, 40, 80)
    pdf.set_line_width(0.4)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_text_color(0, 0, 0)


def add_section(pdf, heading, body_lines):
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(230, 237, 250)
    pdf.set_x(10)
    pdf.cell(W, 7, f"  {heading}", border=0, fill=True, **NL)
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 9)
    for line in body_lines:
        pdf.set_x(10)
        pdf.multi_cell(W, 5, line)
    pdf.ln(3)


def add_table(pdf, headers, rows):
    col_w = W // len(headers)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(20, 40, 80)
    pdf.set_text_color(255, 255, 255)
    for h in headers:
        pdf.cell(col_w, 7, h, border=1, fill=True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    for i, row in enumerate(rows):
        if i % 2 == 0:
            pdf.set_fill_color(244, 248, 255)
        else:
            pdf.set_fill_color(255, 255, 255)
        for cell in row:
            pdf.cell(col_w, 6, str(cell), border=1, fill=True)
        pdf.ln()
    pdf.ln(4)


# ─── OEM XR-900 Pump Manual ───────────────────────────────────────────────────

def create_pump_manual():
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(10, 12, 10)
    pdf.set_auto_page_break(auto=True, margin=12)

    # ── Page 1: Overview & Specifications ──
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(20, 40, 80)
    pdf.set_x(10)
    pdf.cell(W, 12, "FlowServe XR-900 Centrifugal Pump", **NL, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(10)
    pdf.cell(W, 5, "Operation, Maintenance and Diagnostic Manual  |  Rev 4.2", **NL, align="C")
    pdf.set_x(10)
    pdf.cell(W, 5, "Tag Reference: P-101  |  Functional Area: Cooling Infrastructure", **NL, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    add_section(pdf, "1. Product Overview", [
        "The FlowServe XR-900 is a heavy-duty centrifugal pump for continuous industrial cooling.",
        "It is engineered for high-temperature fluid transfer in manufacturing and process environments.",
        "The XR-900 features a dual-mechanical seal, corrosion-resistant impeller housing,",
        "and integrated vibration sensor mounts compatible with ISO 10816-3 standard monitoring.",
        "Model: XR-900  |  Manufacturer: FlowServe  |  Asset Tag: P-101",
    ])

    add_section(pdf, "2. Technical Specifications", [])
    add_table(pdf,
        ["Parameter", "Specification", "Unit"],
        [
            ["Rated Flow Rate",        "450",                   "m3/hr"],
            ["Max Operating Pressure", "12.5",                  "bar"],
            ["Rated Speed",            "2950",                  "RPM"],
            ["Motor Power",            "75",                    "kW"],
            ["Impeller Diameter",      "320",                   "mm"],
            ["Shaft Torque (rated)",   "243",                   "N.m"],
            ["Shaft Torque (max)",     "310",                   "N.m"],
            ["Operating Temp Range",   "-10 to 180",            "degC"],
            ["NPSH Required",          "4.2",                   "m"],
            ["Bearing Type",           "SKF 6316",              "-"],
            ["Seal Type",              "Dual mechanical Type-B","-"],
            ["Base Emissions CO2",     "45",                    "ppm"],
        ]
    )

    add_section(pdf, "3. Installation Requirements", [
        "Mounting: Install on level concrete base with anchor bolts torqued to 80 N.m.",
        "Alignment: Max shaft misalignment 0.05 mm radial, 0.02 mm angular.",
        "Upstream Valve: Isolation valve V-20 (Swagelok V-LOK-2) must be installed on suction line.",
        "  V-20 controls flow into P-101 and is critical for priming and cavitation prevention.",
        "  IMPORTANT: V-20 must be fully open during normal pump operation.",
        "  A closed or partially closed V-20 will restrict inlet flow and cause cavitation in P-101.",
        "Discharge: Downstream feeds into Boiler B-04 heat exchanger feed line.",
        "  P-101 is the sole feed pump for B-04.",
        "  If P-101 goes offline, B-04 must shut down within 8 minutes to prevent thermal runaway.",
    ])

    # ── Page 2: Maintenance & Diagnostics ──
    pdf.add_page()
    add_heading(pdf, "XR-900 Maintenance and Diagnostic Guide")

    add_section(pdf, "4. Scheduled Maintenance Intervals", [])
    add_table(pdf,
        ["Interval", "Task", "Ref"],
        [
            ["250 hrs",  "Lubricate bearing housing with Shell Gadus S2 V220",      "PM-XR9-001"],
            ["500 hrs",  "Inspect mechanical seal for leakage; replace if weeping", "PM-XR9-002"],
            ["1000 hrs", "Full impeller inspection; measure wear ring clearance",    "PM-XR9-003"],
            ["2000 hrs", "Replace shaft bearing set (SKF 6316)",                    "PM-XR9-004"],
            ["5000 hrs", "Full pump overhaul: impeller, seals, bearings, coupling", "PM-XR9-005"],
        ]
    )

    add_section(pdf, "5. Vibration Diagnostic Guide", [
        "Baseline vibration at rated load: 1.8 mm/s RMS.",
        "Alarm threshold: 4.5 mm/s.  Trip threshold: 7.1 mm/s.",
        "",
        "SYMPTOM: Elevated vibration (3 to 6 mm/s) during high thermal load periods.",
        "ROOT CAUSE: Partial flow starvation because upstream valve V-20 is partially closed.",
        "  Under high thermal load the fluid density drops, increasing required NPSH.",
        "  If V-20 is not fully open, available NPSH falls below required 4.2 m causing cavitation.",
        "  Cavitation produces high-frequency vibration in the 1 to 10 kHz band.",
        "",
        "CORRECTIVE ACTION:",
        "  1. Check upstream valve V-20 (Swagelok V-LOK-2 on suction line).",
        "  2. If V-20 is less than fully open, open it to 100% via handwheel.",
        "     Standard correction: open V-20 by 1.5 to 2.0 full rotations counterclockwise.",
        "  3. Monitor vibration for 5 minutes. Should return below 2.0 mm/s.",
        "  4. If vibration persists after V-20 check, inspect seal per PM-XR9-002.",
        "",
        "SYMPTOM: Flow rate drop below 300 m3/hr.",
        "ROOT CAUSE A: V-20 closed or restricted. Check and correct immediately.",
        "ROOT CAUSE B: Impeller wear. Schedule PM-XR9-003 if V-20 is fully open.",
        "",
        "SYMPTOM: Overheating, bearing housing temperature above 85 degC.",
        "CAUSE: Lubrication failure or misalignment causing excessive radial load.",
        "ACTION: Lubricate per PM-XR9-001. Verify coupling alignment.",
    ])

    add_section(pdf, "6. Emergency Shutdown Procedure", [
        "Initiate emergency shutdown if:",
        "  - Vibration exceeds 7.1 mm/s trip threshold",
        "  - Bearing temperature exceeds 95 degC",
        "  - Mechanical seal leak detected",
        "  - Discharge pressure drops more than 40% below rated for more than 30 seconds",
        "",
        "SHUTDOWN STEPS:",
        "  1. Close discharge valve before stopping motor.",
        "  2. De-energize motor via local isolator.",
        "  3. Close upstream valve V-20 to isolate pump from suction line.",
        "  4. Notify B-04 boiler operator: P-101 shutdown removes coolant feed to B-04.",
        "     B-04 must initiate controlled shutdown within 8 minutes.",
        "  5. Log incident in CMMS with vibration readings and timestamp.",
    ])

    # ── Page 3: Bolt Torque & Integration Notes ──
    pdf.add_page()
    add_heading(pdf, "XR-900 Torque Reference and Process Integration")

    add_section(pdf, "7. Bolt Torque Specifications", [])
    add_table(pdf,
        ["Location", "Bolt Size", "Torque (N.m)", "Pattern"],
        [
            ["Casing split bolts",    "M20", "180", "Cross pattern"],
            ["Bearing housing",       "M16", "110", "Star pattern"],
            ["Impeller lock nut",     "M30", "420", "Single"],
            ["Mechanical seal gland", "M12", "45",  "Even cross"],
            ["Base plate anchor",     "M24", "310", "All corners first"],
            ["Coupling hub bolts",    "M16", "130", "Alternating"],
            ["Suction flange (V-20)", "M20", "165", "Cross pattern"],
            ["Discharge flange",      "M20", "165", "Cross pattern"],
        ]
    )

    add_section(pdf, "8. Process Integration Notes", [
        "P-101 is part of a three-component cooling loop:",
        "",
        "  [V-20 Swagelok V-LOK-2] --> [P-101 FlowServe XR-900] --> [B-04 Thermax BLR-MAX]",
        "         upstream                                                   downstream",
        "",
        "V-20 is the primary flow control and isolation point for P-101 suction line.",
        "P-101 is the sole coolant feed pump for the Thermax BLR-MAX boiler (B-04).",
        "B-04 generates 320 ppm CO2 equivalent under full load.",
        "",
        "OPERATIONAL DEPENDENCY CHAIN:",
        "  If V-20 is closed or restricted: P-101 cavitates or loses flow.",
        "  If P-101 trips: B-04 loses coolant feed and must shut down within 8 minutes.",
        "  If B-04 shuts down: Power-Gen functional area loses primary steam source.",
        "",
        "All maintenance on any component in this chain requires coordination across",
        "Cooling and Power-Gen areas. A permit-to-work must be raised for both areas.",
    ])

    add_section(pdf, "9. Spare Parts Minimum Stock", [])
    add_table(pdf,
        ["Part Number", "Description", "Min Qty"],
        [
            ["XR9-IMP-320",  "Impeller assembly, 320mm, S316 steel",  "1"],
            ["XR9-SEAL-B",   "Dual mechanical seal kit, Type-B",       "2"],
            ["XR9-BRG-6316", "Shaft bearing set, SKF 6316",            "2"],
            ["XR9-WR-CLR",   "Wear ring set (suction + discharge)",    "2"],
            ["XR9-CPL-FLX",  "Flexible coupling element, 75kW rated", "1"],
        ]
    )

    out = os.path.join(OUTPUT_DIR, "OEM-XR-900-Pump-Manual.pdf")
    pdf.output(out)
    print(f"Created: {out}  ({os.path.getsize(out):,} bytes)")


# ─── Tribal Knowledge — Bob's Field Notes ─────────────────────────────────────

def create_tribal_notes():
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(10, 12, 10)
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(120, 40, 10)
    pdf.set_x(10)
    pdf.cell(W, 10, "Field Operator Knowledge Record", **NL, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(10)
    pdf.cell(W, 5, "Operator: Bob Patil  |  Senior Maintenance Tech (22 years)", **NL, align="C")
    pdf.set_x(10)
    pdf.cell(W, 5, "Date Recorded: 2026-03-14  |  Area: Cooling Infrastructure", **NL, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    add_section(pdf, "Observation 1: Pump P-101 Vibration and Valve V-20 Root Cause", [
        "I have been working on this pump for fifteen years and I can tell you for certain.",
        "Every single time P-101 starts vibrating badly during hot weather or high thermal loads,",
        "it is because valve V-20 is not fully open. The previous shift tends to partially close it",
        "during line checks and forgets to re-open it. The fix is simple: go to valve V-20 handwheel",
        "and open it two full rotations counterclockwise. Within five minutes the vibration drops",
        "completely and the pump settles to normal. I have done this over forty times in fifteen years.",
        "Do not schedule a full teardown until you have checked V-20 first.",
        "",
        "Asset: P-101 (PUMP-101)  |  Upstream valve: V-20 (VALVE-020)",
        "Issue: Vibration under high thermal load",
        "Fix: Open V-20 two full rotations counterclockwise",
        "Confidence: HIGH (40+ occurrences confirmed over 15 years)",
    ])

    add_section(pdf, "Observation 2: Boiler B-04 Has No Backup Feed Pump", [
        "People forget that B-04 has no backup feed pump. If P-101 goes down for any reason,",
        "you have eight minutes before the boiler overheats. In practice during summer above",
        "38 degrees Celsius ambient, it is more like five to six minutes. When P-101 alarms,",
        "the boiler team must be notified immediately by radio. There is no automatic interlock.",
        "The interlock was deferred in the 2019 upgrade. Pending work order: WO-2019-0847.",
        "",
        "Asset: B-04 (BOILER-04)  |  Feed pump: P-101",
        "Risk: No automatic P-101-trip to B-04-shutdown interlock",
        "Action: Manual radio call required within 5 to 8 minutes of P-101 trip",
        "Pending: WO-2019-0847",
    ])

    add_section(pdf, "Observation 3: Valve V-20 Stiff Handwheel Since 2024", [
        "The handwheel on V-20 has been stiff since the 2024 annual shutdown. They replaced the",
        "packing but did not properly torque the gland follower. You need two hands to turn it.",
        "Use the extended handle T-EXT-044 from the C-block tool cabinet, second shelf.",
        "Without it you need two operators to turn V-20 in an emergency, which is a safety issue.",
        "",
        "Asset: V-20 (VALVE-020)",
        "Issue: Stiff handwheel due to improperly torqued gland follower after 2024 packing job",
        "Workaround: Extended handle T-EXT-044, C-block tool cabinet, shelf 2",
    ])

    add_section(pdf, "Observation 4: B-04 Emissions Spike Above 80 Percent Load", [
        "When B-04 runs above 80 percent capacity during winter peak demand, CO2 emissions",
        "climb well above the baseline 320 ppm. I have seen 410 ppm on cold days when all three",
        "boilers run together. The sensor has a 6-second lag so real peak is probably higher.",
        "Someone should verify the permit limit from the 2025 environmental compliance review.",
        "",
        "Asset: B-04 (BOILER-04)",
        "Baseline: 320 ppm CO2  |  Observed peak: ~410 ppm at above 80% load",
        "Sensor lag: 6 seconds. Real peak likely higher.",
    ])

    out = os.path.join(OUTPUT_DIR, "Tribal-Bob-Notes.pdf")
    pdf.output(out)
    print(f"Created: {out}  ({os.path.getsize(out):,} bytes)")


if __name__ == "__main__":
    create_pump_manual()
    create_tribal_notes()
    print("\nAll demo documents created in data/docs/")
