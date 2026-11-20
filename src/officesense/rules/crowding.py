

class CrowdingRule:
    def __init__(self, max_people=6, min_duration_s=8):
        self.max_people = max_people
        self.min_duration_s = min_duration_s

        # Track crowding state separately for each camera.
        self.states = {}

    def evaluate(self, camera_id, people_count, video_time_s, event_ts):
        """
        Evaluate crowding for one processed frame.

        video_time_s: elapsed time in the source video.
        event_ts: timestamp associated with the processed frame.
        """

        state = self.states.get(camera_id)

        # The crowding condition is no longer true.
        if people_count <= self.max_people:
            self.states[camera_id] = None
            return None

        # Start monitoring when the count first exceeds the limit.
        if state is None:
            self.states[camera_id] = {
                "start_video_time": video_time_s,
                "started": event_ts,
                "alerted": False
            }
            return None

        # Don't generate repeated events while the condition persists.
        if state["alerted"]:
            return None

        duration = video_time_s - state["start_video_time"]

        # Trigger only after the required duration.
        if duration >= self.min_duration_s:
            state["alerted"] = True

            return {
                "rule_id": "crowding-camera",
                "severity": "warning",
                "status": "open",
                "started": state["started"],
                "camera_id": camera_id,
                "zone": "camera_view",
                "details": {
                    "count": people_count,
                    "limit": self.max_people,
                    "duration_s": round(duration, 2)
                }
            }

        return None
