import os
import json
import pandas as pd

os.makedirs("data", exist_ok=True)

# 1. Baseline Schedule CSV for Oil India Limited (Duliajan - Numaligarh Pipeline Terminal)
baseline_csv = """Activity_ID,WBS_Level,WBS_Code,Activity_Name,Discipline,Planned_Start,Planned_Finish,Planned_Duration_Days,Predecessors,Weightage,Unit_Area
ACT-CIV-001,L5,1.1.1,Clear Site and Mobilize Excavation Equipment,Civil,2026-10-01,2026-10-05,5,,2.0,Tank Farm Area
ACT-CIV-002,L5,1.1.2,Excavation and Soil Compaction for Pump House Foundation,Civil,2026-10-06,2026-10-14,9,ACT-CIV-001,4.5,Pump House
ACT-CIV-003,L6,1.1.3,Rebar Binding and Shuttering for Foundation Pad P-12,Civil,2026-10-15,2026-10-21,7,ACT-CIV-002,3.5,Pump House
ACT-CIV-004,L6,1.1.4,Pour M35 Reinforced Concrete for Foundation Pad P-12,Civil,2026-10-22,2026-10-25,4,ACT-CIV-003,4.0,Pump House
ACT-CIV-005,L5,1.1.5,Curing and Foundation Inspection Pad P-12,Civil,2026-10-26,2026-11-02,8,ACT-CIV-004,2.0,Pump House
ACT-CIV-006,L5,1.2.1,Excavate and Cast Crude Storage Tank TK-101 Ring Beam Foundation,Civil,2026-10-10,2026-10-28,19,ACT-CIV-001,6.0,Tank Farm Area
ACT-CIV-007,L6,1.3.1,Excavate Underground Cable Trench Corridor C-1,Civil,2026-10-16,2026-10-24,9,ACT-CIV-001,2.5,Substation Yard
ACT-EQP-001,L5,2.1.1,Erect and Grout Main Crude Booster Pump P-101A on Pad P-12,Mechanical,2026-11-03,2026-11-10,8,ACT-CIV-005,5.0,Pump House
ACT-EQP-002,L5,2.1.2,Erect and Grout Standby Crude Booster Pump P-101B on Pad P-12,Mechanical,2026-11-08,2026-11-15,8,ACT-CIV-005,5.0,Pump House
ACT-EQP-003,L5,2.2.1,Plate Erection and Welding for Crude Storage Tank TK-101,Mechanical,2026-10-29,2026-11-25,28,ACT-CIV-006,8.0,Tank Farm Area
ACT-PIP-101,L5,3.1.1,Fabricate Line 24-CW-001 24-inch Crude Oil Pipe Spools,Piping,2026-10-15,2026-10-30,16,,4.0,Fab Yard
ACT-PIP-102,L6,3.1.2,NDT and Hydrotest Fabricated Spools for Line 24-CW-001,Piping,2026-10-31,2026-11-05,6,ACT-PIP-101,2.5,Fab Yard
ACT-PIP-103,L5,3.1.3,Install Pipe Rack Steel Support Module PR-04,Piping,2026-10-20,2026-10-30,11,ACT-CIV-002,3.0,Manifold Yard
ACT-PIP-104,L6,3.1.4,Erect Line 24-CW-001 Spool on Pipe Rack PR-04,Piping,2026-11-06,2026-11-16,11,ACT-PIP-102;ACT-PIP-103,6.5,Manifold Yard
ACT-PIP-105,L6,3.1.5,Fit-up and Weld Golden Joint GJ-04 on Line 24-CW-001,Piping,2026-11-17,2026-11-22,6,ACT-PIP-104,3.0,Manifold Yard
ACT-PIP-106,L5,3.2.1,Erect Line 16-DIS-002 Discharge Manifold to Pump P-101A,Piping,2026-11-11,2026-11-20,10,ACT-EQP-001,4.5,Pump House
ACT-PIP-107,L5,3.2.2,Erect Line 16-DIS-003 Discharge Manifold to Pump P-101B,Piping,2026-11-16,2026-11-25,10,ACT-EQP-002,4.5,Pump House
ACT-PIP-108,L5,3.3.1,System Hydrostatic Pressure Testing for Line 24-CW-001,Piping,2026-11-23,2026-11-28,6,ACT-PIP-105,4.0,Manifold Yard
ACT-ELE-201,L5,4.1.1,Lay Sand Bedding and Pull 11kV Power Feeder Cable in Cable Tray B,Electrical,2026-10-25,2026-11-05,12,ACT-CIV-007,4.0,Substation Yard
ACT-ELE-202,L6,4.1.2,Terminate 11kV Feeder Cable at Motor Control Center MCC-01,Electrical,2026-11-06,2026-11-12,7,ACT-ELE-201,3.0,Substation Yard
ACT-ELE-203,L5,4.2.1,Hook up Power Supply Cable to Booster Pump Motor P-101A,Electrical,2026-11-13,2026-11-18,6,ACT-EQP-001;ACT-ELE-202,3.5,Pump House
ACT-ELE-204,L5,4.2.2,Install Substation Earthing Grid and Grounding Rods,Electrical,2026-10-20,2026-11-01,13,ACT-CIV-007,3.0,Substation Yard
ACT-INS-301,L5,5.1.1,Install Ultrasonic Flow Meter FT-101 on Line 24-CW-001,Instrumentation,2026-11-18,2026-11-24,7,ACT-PIP-104,3.0,Manifold Yard
ACT-INS-302,L6,5.1.2,Run Twisted Shielded Instrument Signal Cable to PLC Cabinet,Instrumentation,2026-11-15,2026-11-22,8,ACT-ELE-201,3.0,Control Room
ACT-INS-303,L5,5.2.1,Calibrate Pressure Transmitter PT-204 at Pump Discharge,Instrumentation,2026-11-21,2026-11-26,6,ACT-PIP-106,2.5,Pump House
ACT-HSE-401,L5,6.1.1,Install Deluge Fire Protection Spray Piping and Hydrant Ring,HSE,2026-11-01,2026-11-20,20,ACT-CIV-006,4.0,Tank Farm Area
ACT-COM-501,L4,7.1.1,Integrated Hydrocarbon Pre-Commissioning and Loop Check,Commissioning,2026-11-29,2026-12-08,10,ACT-PIP-108;ACT-ELE-203;ACT-INS-301,6.0,Plant Wide
"""
with open("data/baseline_schedule_oil_india.csv", "w", encoding="utf-8") as f:
    f.write(baseline_csv.strip())

# 2. Baseline Schedule XML (Primavera P6 export format)
baseline_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Project xmlns="http://www.primavera.com/pm/xml">
  <ProjectHeader>
    <ProjectId>OIL-DUL-026</ProjectId>
    <ProjectName>Duliajan-Numaligarh Crude Oil Pumping Station &amp; Pipeline Terminal</ProjectName>
    <Organization>Oil India Limited</Organization>
    <CreationDate>2026-09-15T00:00:00</CreationDate>
  </ProjectHeader>
  <Activities>
    <Activity>
      <Id>ACT-CIV-001</Id>
      <Name>Clear Site and Mobilize Excavation Equipment</Name>
      <WBSCode>1.1.1</WBSCode>
      <Discipline>Civil</Discipline>
      <PlannedStartDate>2026-10-01</PlannedStartDate>
      <PlannedFinishDate>2026-10-05</PlannedFinishDate>
      <DurationDays>5</DurationDays>
      <Weightage>2.0</Weightage>
    </Activity>
    <Activity>
      <Id>ACT-PIP-104</Id>
      <Name>Erect Line 24-CW-001 Spool on Pipe Rack PR-04</Name>
      <WBSCode>3.1.4</WBSCode>
      <Discipline>Piping</Discipline>
      <PlannedStartDate>2026-11-06</PlannedStartDate>
      <PlannedFinishDate>2026-11-16</PlannedFinishDate>
      <DurationDays>11</DurationDays>
      <Predecessors>ACT-PIP-102;ACT-PIP-103</Predecessors>
      <Weightage>6.5</Weightage>
    </Activity>
    <Activity>
      <Id>ACT-ELE-201</Id>
      <Name>Lay Sand Bedding and Pull 11kV Power Feeder Cable in Cable Tray B</Name>
      <WBSCode>4.1.1</WBSCode>
      <Discipline>Electrical</Discipline>
      <PlannedStartDate>2026-10-25</PlannedStartDate>
      <PlannedFinishDate>2026-11-05</PlannedFinishDate>
      <DurationDays>12</DurationDays>
      <Predecessors>ACT-CIV-007</Predecessors>
      <Weightage>4.0</Weightage>
    </Activity>
  </Activities>
</Project>
"""
with open("data/baseline_schedule_oil_india.xml", "w", encoding="utf-8") as f:
    f.write(baseline_xml.strip())

# 3. Unstructured DPR (Daily Progress Report) with site idioms & field jargon
dpr_text = """================================================================================
OIL INDIA LIMITED - INFRASTRUCTURE PROJECT MONITORING
DAILY PROGRESS REPORT (DPR) #142
Project: Duliajan to Numaligarh Crude Dispatch Terminal (PS-04)
Report Date: 2026-11-08 | Shift: Day Shift (07:00 - 18:00)
Weather: Overcast with morning drizzle (temp 24C) | Manpower at Site: 64 pax
================================================================================

1. CIVIL ENGINEERING DISCIPLINE:
- Pump House Area: Foundation Pad P-12 curing concluded today. QC team issued clearance certificate after 7-day wet burlap test. Formwork stripped and backfilling commenced.
- Tank Farm Area: Crude Storage Tank TK-101 ring beam foundation excavation reached 70% depth. Rain slowed muck disposal by 2 hours.
- Substation Corridor: Cable trench excavation C-1 completed up to chainage 0+240.

2. PIPING & MECHANICAL DISCIPLINE:
- Manifold Yard: Piping crew mobilized at Pipe Rack PR-04. Erection of 24-inch crude oil spools on line 24-CW-001 in progress. 
  Specific progress: 6 out of 8 spools placed and pinned on steel brackets (approx 75% complete).
  Delay Notice: Further spool placement halted at 15:30 due to hydraulic line rupture on 50T mobile crane. Crane vendor technician called for spare replacement hose.
- Pump House: Booster Pump P-101A baseplate aligned and grouting started using Conbextra GP2 non-shrink grout.

3. ELECTRICAL & INSTRUMENTATION:
- Substation Yard: Laying sand bedding and pulling 11kV HT power cable along Tray B. Pulled 240 meters out of 500m total run. 
- Control Room: PLC cabinet marshalling rack arrived. Unpacking and tagging started.

4. HEALTH, SAFETY & ENVIRONMENT (HSE):
- Zero LTI reported. Tool Box Talk conducted on crane rigging safety and heavy lift rigging protocols. 1 near-miss logged (loose sling shackle).

5. CRITICAL BOTTLENECKS & DELAY CALLOUTS:
[DELAY-01] Category: Operational | Spool erection on line 24-CW-001 stopped early due to mobile crane hydraulic failure. Estimated recovery: 24 hours.
[DELAY-02] Category: Material | Flange gaskets for discharge manifold 16-DIS-002 pending dispatch from Guwahati warehouse.
"""
with open("data/dpr_sample_civil_piping.txt", "w", encoding="utf-8") as f:
    f.write(dpr_text.strip())

# 4. Piping Discipline Excel Spreadsheet
piping_data = [
    {"Date": "2026-11-06", "Line_Number": "24-CW-001", "Spool_ID": "SP-101", "Rack_Ref": "PR-04", "Field_Status": "Erected & Bolted", "Progress_Pct": 15, "Welder_ID": "W-04", "Remarks": "First spool hung on bay 1"},
    {"Date": "2026-11-07", "Line_Number": "24-CW-001", "Spool_ID": "SP-102 & 103", "Rack_Ref": "PR-04", "Field_Status": "Erected & Bolted", "Progress_Pct": 45, "Welder_ID": "W-04", "Remarks": "Two spools lifted and leveled"},
    {"Date": "2026-11-08", "Line_Number": "24-CW-001", "Spool_ID": "SP-104, 105, 106", "Rack_Ref": "PR-04", "Field_Status": "In Progress (6/8 spools)", "Progress_Pct": 75, "Welder_ID": "W-08", "Remarks": "Stopped at 15:30 due to crane breakdown"},
    {"Date": "2026-11-09", "Line_Number": "16-DIS-002", "Spool_ID": "SP-DIS-01", "Rack_Ref": "PH-01", "Field_Status": "Fit-up on hold", "Progress_Pct": 10, "Welder_ID": "W-12", "Remarks": "Waiting for 300# ANSI spiral wound gasket"},
    {"Date": "2026-11-08", "Line_Number": "24-CW-001", "Spool_ID": "GJ-04", "Rack_Ref": "PR-04", "Field_Status": "Not Started", "Progress_Pct": 0, "Welder_ID": "W-04", "Remarks": "Golden joint awaiting remaining 2 spools"},
]
df_piping = pd.DataFrame(piping_data)
df_piping.to_excel("data/piping_spool_erection_log.xlsx", index=False)

# 5. Civil Discipline Excel Spreadsheet
civil_data = [
    {"Pour_Date": "2026-10-22", "Foundation_Tag": "Pad P-12", "Location": "Pump House", "Activity_Desc": "Poured M35 concrete (45 m3)", "QC_Inspection": "Passed", "Curing_Days": 1, "Status": "In Progress"},
    {"Pour_Date": "2026-10-26", "Foundation_Tag": "Pad P-12", "Location": "Pump House", "Activity_Desc": "Curing and cylinder test 7-day", "QC_Inspection": "Passed", "Curing_Days": 5, "Status": "In Progress"},
    {"Pour_Date": "2026-11-02", "Foundation_Tag": "Pad P-12", "Location": "Pump House", "Activity_Desc": "Final curing & NDT rebound hammer check", "QC_Inspection": "Certified OK", "Curing_Days": 8, "Status": "Completed"},
    {"Pour_Date": "2026-11-08", "Foundation_Tag": "Ring Beam TK-101", "Location": "Tank Farm", "Activity_Desc": "Excavation and blinding concrete", "QC_Inspection": "Under Inspection", "Curing_Days": 0, "Status": "65% Completed"},
    {"Pour_Date": "2026-10-24", "Foundation_Tag": "Trench C-1", "Location": "Substation", "Activity_Desc": "Excavate underground electrical trench", "QC_Inspection": "Passed", "Curing_Days": 0, "Status": "Completed"},
]
df_civil = pd.DataFrame(civil_data)
df_civil.to_excel("data/civil_foundation_log.xlsx", index=False)

# 6. Supervisor Voice Transcripts (Realistic voice notes from site engineers)
voice_transcripts = [
    {
        "supervisor": "Raman Borah",
        "discipline": "Piping",
        "timestamp": "2026-11-08T16:15:00+05:30",
        "location": "Manifold Yard Rack 4",
        "audio_clip_id": "VOICE-PIP-0811-01",
        "transcript": "Hello control room, Raman here from Piping. We have completed spool erection on line 24-CW-001 up to spool SP-106 on rack 4. Out of 8 spools, 6 are erected and bolted. Remaining two cannot be lifted today because the 50-ton mobile crane hydraulic line ruptured. Crane mechanic is on site, expecting hose replacement by tomorrow 10 AM. Current progress roughly seventy-five percent.",
        "expected_link": "ACT-PIP-104"
    },
    {
        "supervisor": "Debojit Saikia",
        "discipline": "Civil",
        "timestamp": "2026-11-08T17:30:00+05:30",
        "location": "Pump House",
        "audio_clip_id": "VOICE-CIV-0811-02",
        "transcript": "Civil supervisor Debojit reporting. Curing and final foundation inspection for Booster Pump Pad P-12 is hundred percent complete today. Client QC has signed off the test cube reports. Mechanical team can take over for pump positioning anytime from tomorrow.",
        "expected_link": "ACT-CIV-005"
    },
    {
        "supervisor": "Bikash Gogoi",
        "discipline": "Electrical",
        "timestamp": "2026-11-08T18:00:00+05:30",
        "location": "Substation Yard",
        "audio_clip_id": "VOICE-ELE-0811-03",
        "transcript": "Bikash from Electrical side. We pulled two hundred and forty meters of eleven kV power cable in tray B along the trench today. Total run is five hundred meters, so progress is about forty-eight percent. Sand bedding was laid in the morning shift.",
        "expected_link": "ACT-ELE-201"
    },
    {
        "supervisor": "Anup Baruah",
        "discipline": "Piping",
        "timestamp": "2026-11-09T11:00:00+05:30",
        "location": "Pump House Discharge",
        "audio_clip_id": "VOICE-PIP-0911-04",
        "transcript": "Piping crew tried to start fit-up of pump discharge line 16-DIS-002, but the required three hundred pound spiral wound gaskets have not arrived from store. Activity is stalled waiting for material clearance.",
        "expected_link": "ACT-PIP-106"
    }
]
with open("data/supervisor_voice_transcripts.json", "w", encoding="utf-8") as f:
    json.dump(voice_transcripts, f, indent=2)

print("Sample datasets generated successfully in ./data!")
