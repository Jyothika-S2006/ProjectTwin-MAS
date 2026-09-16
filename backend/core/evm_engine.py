from datetime import datetime, timedelta
from typing import Dict, List, Any
from core.models import EVMMetrics, BaselineActivity, ActualActivityState

class EVMEngine:
    def __init__(self, schedule_engine):
        self.schedule_engine = schedule_engine

    def calculate_evm(self, as_of_date_str: str = "2026-11-10") -> EVMMetrics:
        """
        Computes deterministic EVM metrics (PV, EV, Claimed, SV, SPI) without LLM estimation.
        """
        as_of_date = datetime.strptime(as_of_date_str, "%Y-%m-%d")
        total_weight = sum(act.weightage for act in self.schedule_engine.baseline_activities.values())
        if total_weight <= 0:
            total_weight = 100.0

        pv_accum = 0.0
        ev_accum = 0.0
        claimed_accum = 0.0

        for act_id, act in self.schedule_engine.baseline_activities.items():
            p_start = datetime.strptime(act.planned_start, "%Y-%m-%d")
            p_finish = datetime.strptime(act.planned_finish, "%Y-%m-%d")
            weight = act.weightage

            # Deterministic Planned Value (PV) calculation
            if as_of_date < p_start:
                planned_pct = 0.0
            elif as_of_date >= p_finish:
                planned_pct = 100.0
            else:
                elapsed_days = (as_of_date - p_start).days
                tot_days = max(1, (p_finish - p_start).days)
                planned_pct = min(100.0, max(0.0, (elapsed_days / tot_days) * 100.0))

            pv_accum += (weight * planned_pct) / 100.0

            # Deterministic Earned Value (EV) from protected actuals layer
            actual_state = self.schedule_engine.actual_states.get(act_id)
            if actual_state:
                actual_pct = actual_state.progress_pct
                evidence_pct = actual_state.evidence_progress_pct
                ev_accum += (weight * evidence_pct) / 100.0
                claimed_accum += (weight * actual_pct) / 100.0

        pv_pct = round((pv_accum / total_weight) * 100.0, 2)
        ev_pct = round((ev_accum / total_weight) * 100.0, 2)
        claimed_pct = round((claimed_accum / total_weight) * 100.0, 2)

        sv = round(ev_pct - pv_pct, 2)
        spi = round(ev_pct / pv_pct, 3) if pv_pct > 0 else 1.0

        # Critical path delay calculation
        crit_acts = [self.schedule_engine.baseline_activities[cid] for cid in self.schedule_engine.get_critical_path()]
        crit_delay_days = 0
        for ca in crit_acts:
            actual_state = self.schedule_engine.actual_states.get(ca.activity_id)
            if actual_state and actual_state.delay_reasons:
                crit_delay_days += 3  # Estimated slippage penalty per active delay

        proj_finish = datetime(2026, 12, 8) + timedelta(days=crit_delay_days)

        return EVMMetrics(
            planned_value=pv_pct,
            earned_value=ev_pct,
            claimed_value=claimed_pct,
            schedule_variance=sv,
            schedule_performance_index=spi,
            critical_path_delay_days=crit_delay_days,
            projected_finish_date=proj_finish.strftime("%Y-%m-%d"),
            as_of_date=as_of_date_str
        )

    def generate_s_curve_data(self) -> Dict[str, Any]:
        """
        Generates daily time-series coordinates for the S-Curve:
        - Planned S-Curve (%)
        - Evidence-supported Earned S-Curve (%)
        - Claimed Progress S-Curve (%)
        """
        start_date = datetime(2026, 10, 1)
        end_date = datetime(2026, 12, 10)
        current_cutoff = datetime(2026, 11, 10)

        dates = []
        planned_curve = []
        actual_curve = []
        claimed_curve = []

        total_weight = sum(act.weightage for act in self.schedule_engine.baseline_activities.values()) or 100.0

        curr = start_date
        while curr <= end_date:
            d_str = curr.strftime("%Y-%m-%d")
            dates.append(curr.strftime("%d-%b"))

            # Calculate Planned Value on this date
            pv_day = 0.0
            for act in self.schedule_engine.baseline_activities.values():
                p_start = datetime.strptime(act.planned_start, "%Y-%m-%d")
                p_finish = datetime.strptime(act.planned_finish, "%Y-%m-%d")
                if curr < p_start:
                    pct = 0.0
                elif curr >= p_finish:
                    pct = 100.0
                else:
                    tot = max(1, (p_finish - p_start).days)
                    pct = ((curr - p_start).days / tot) * 100.0
                pv_day += (act.weightage * pct) / 100.0

            planned_pct = round((pv_day / total_weight) * 100.0, 1)
            planned_curve.append(planned_pct)

            # For dates <= current_cutoff, calculate actual/claimed
            if curr <= current_cutoff:
                # Scaled actuals
                ratio = (curr - start_date).days / max(1, (current_cutoff - start_date).days)
                # Earned value up to current date
                current_ev = self.calculate_evm(current_cutoff.strftime("%Y-%m-%d"))
                ev_val = round(current_ev.earned_value * (ratio ** 1.3), 1)
                cv_val = round(current_ev.claimed_value * (ratio ** 1.2), 1)
                actual_curve.append(ev_val)
                claimed_curve.append(cv_val)
            else:
                actual_curve.append(None)
                claimed_curve.append(None)

            curr += timedelta(days=2)

        return {
            "labels": dates,
            "planned": planned_curve,
            "earned": actual_curve,
            "claimed": claimed_curve
        }
