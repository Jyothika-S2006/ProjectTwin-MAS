import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "projecttwin_memory.db")

class InstitutionalMemoryEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()
        self._seed_historical_benchmarks()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historical_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT,
                    activity_code TEXT,
                    activity_name TEXT,
                    discipline TEXT,
                    planned_duration INTEGER,
                    actual_duration INTEGER,
                    variance_days INTEGER,
                    variance_pct REAL,
                    delay_category TEXT,
                    delay_cause TEXT,
                    productivity_ratio REAL,
                    terrain_weather TEXT,
                    lessons_learned TEXT
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS delay_taxonomy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    subcategory TEXT,
                    mitigation_recommendation TEXT
                );
            """)
            conn.commit()

    def _seed_historical_benchmarks(self):
        """Pre-populates institutional memory with past Oil India infrastructure project lessons."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM historical_activities;")
            if cursor.fetchone()[0] == 0:
                historical_seeds = [
                    (
                        "Duliajan Tank Farm Expansion (Ph-1)", "ACT-PIP-104", 
                        "Erect 24-inch Spool on Pipe Rack", "Piping", 
                        11, 15, 4, 36.4, "Operational", "Mobile crane breakdown & hydraulic hose replacement delay", 0.73, "Heavy Monsoon",
                        "Always mandate on-site spare hydraulic hoses for >40T cranes during peak erection."
                    ),
                    (
                        "Numaligarh Dispatch Manifold", "ACT-PIP-106", 
                        "Erect Discharge Manifold to Booster Pump", "Piping", 
                        10, 14, 4, 40.0, "Material", "Class 300 ANSI spiral wound gaskets delayed in customs transit", 0.71, "Winter/Clear",
                        "Procure specialized RTJ and spiral-wound gaskets 6 weeks prior to spool mobilization."
                    ),
                    (
                        "Barauni Pumping Station Upgrade", "ACT-CIV-004", 
                        "Pour M35 Reinforced Concrete for Pump Pad P-12", "Civil", 
                        4, 4, 0, 0.0, "None", "Nil - on schedule", 1.0, "Dry Season",
                        "Ready-mix batching plant within 15 km ensured continuous concrete pour without cold joints."
                    ),
                    (
                        "Guwahati Pumping Station", "ACT-CIV-005", 
                        "Curing and Foundation Inspection Pad P-12", "Civil", 
                        8, 10, 2, 25.0, "Approval", "Client third-party inspector unavailable for rebound hammer test", 0.80, "Clear",
                        "Schedule joint inspection window 48 hours prior to 7-day curing threshold."
                    ),
                    (
                        "Duliajan Terminal Electrification", "ACT-ELE-201", 
                        "Pull 11kV Power Feeder Cable in Cable Tray", "Electrical", 
                        12, 16, 4, 33.3, "Operational", "Cable winch slippage and tight bend radius in trench C-1", 0.75, "Overcast",
                        "Utilize motorized cable pulling rollers every 10m to avoid insulation pinch."
                    ),
                    (
                        "Moran Crude Gathering Station", "ACT-CIV-006", 
                        "Excavate & Cast Storage Tank Ring Beam", "Civil", 
                        19, 26, 7, 36.8, "Weather", "Waterlogging in tank foundation trench during flash rains", 0.73, "Monsoon Rain",
                        "Deploy high-capacity dewatering sludge pumps before beginning excavation in Brahmaputra basin."
                    ),
                    (
                        "Naharkatia Metering Station", "ACT-INS-301", 
                        "Install Ultrasonic Flow Meter on Main Header", "Instrumentation", 
                        7, 8, 1, 14.3, "Approval", "Factory Calibration certificate mismatch with P&ID line spec", 0.87, "Clear",
                        "Perform pre-dispatch document verification on all custody-transfer ultrasonic meters."
                    ),
                ]
                cursor.executemany("""
                    INSERT INTO historical_activities (
                        project_name, activity_code, activity_name, discipline,
                        planned_duration, actual_duration, variance_days, variance_pct,
                        delay_category, delay_cause, productivity_ratio, terrain_weather, lessons_learned
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, historical_seeds)

                # Seed Delay Taxonomy
                delays = [
                    ("Material", "Flange Gasket / Fastener Shortage", "Maintain 10% on-site buffer for ANSI 300# gaskets"),
                    ("Material", "Pipe Spool Delivery Delay", "Link spool fabrication tracker to vendor dispatch ERP"),
                    ("Operational", "Mobile Crane Equipment Breakdown", "Pre-qualify crane vendors with 4-hour replacement SLA"),
                    ("Operational", "Cable Pulling Winch Failure", "Use multi-drive automated winch system"),
                    ("Approval", "Third-Party Inspector Clearance", "Implement digital inspection sign-off workflow"),
                    ("Approval", "PTW / Hot Work Permit Delays", "Automate electronic Permit-to-Work issuance"),
                    ("Weather", "Flash Floods & Waterlogging", "Pre-install perimeter trenching and sump pumps"),
                ]
                cursor.executemany("""
                    INSERT INTO delay_taxonomy (category, subcategory, mitigation_recommendation)
                    VALUES (?, ?, ?);
                """, delays)
                conn.commit()

    def record_activity_completion(
        self,
        project_name: str,
        activity_code: str,
        activity_name: str,
        discipline: str,
        planned_duration: int,
        actual_duration: int,
        delay_category: str,
        delay_cause: str,
        weather: str,
        lessons: str
    ):
        variance_days = actual_duration - planned_duration
        variance_pct = round((variance_days / max(1, planned_duration)) * 100.0, 1)
        productivity = round(planned_duration / max(1, actual_duration), 2)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO historical_activities (
                    project_name, activity_code, activity_name, discipline,
                    planned_duration, actual_duration, variance_days, variance_pct,
                    delay_category, delay_cause, productivity_ratio, terrain_weather, lessons_learned
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                project_name, activity_code, activity_name, discipline,
                planned_duration, actual_duration, variance_days, variance_pct,
                delay_category, delay_cause, productivity, weather, lessons
            ))
            conn.commit()

    def get_discipline_productivity_benchmarks(self) -> List[Dict[str, Any]]:
        """Returns aggregated discipline productivity from historical project execution."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    discipline,
                    COUNT(*) as sample_count,
                    ROUND(AVG(planned_duration), 1) as avg_planned_days,
                    ROUND(AVG(actual_duration), 1) as avg_actual_days,
                    ROUND(AVG(variance_pct), 1) as avg_variance_pct,
                    ROUND(AVG(productivity_ratio), 2) as avg_productivity_index
                FROM historical_activities
                GROUP BY discipline;
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_delay_frequency_distribution(self) -> List[Dict[str, Any]]:
        """Returns frequency of root delay categories for forecasting."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    delay_category,
                    COUNT(*) as occurrences,
                    ROUND(AVG(variance_days), 1) as avg_impact_days
                FROM historical_activities
                WHERE delay_category != 'None'
                GROUP BY delay_category
                ORDER BY occurrences DESC;
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def query_historical_patterns(self, query: str = "", discipline: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries institutional memory for execution patterns and lessons learned."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            sql = """
                SELECT * FROM historical_activities 
                WHERE 1=1
            """
            params = []
            if discipline and discipline.lower() != "all":
                sql += " AND LOWER(discipline) = LOWER(?)"
                params.append(discipline)
            if query:
                sql += " AND (activity_name LIKE ? OR delay_cause LIKE ? OR lessons_learned LIKE ?)"
                kw = f"%{query}%"
                params.extend([kw, kw, kw])
            
            sql += " ORDER BY id DESC LIMIT 20;"
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
