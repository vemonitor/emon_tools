"""Emon Fina shared data test"""
from emon_tools.emon_fina.fina_utils import Utils as Ut


class EmonFinaDataTest:
    """Emon Fina shared data test"""
    @staticmethod
    def get_time_start():
        """Get finaMeta data"""
        return int(Ut.get_start_day(1575981140))

    @staticmethod
    def get_time_start_2():
        """Get finaMeta data"""
        return int(Ut.get_start_day(1575981140)) - 33

    @staticmethod
    def get_fina_meta():
        """Get finaMeta data"""
        npoints = 3600 * 24 * 6
        start_time = EmonFinaDataTest.get_time_start()
        return {
            "start_time": start_time,
            "interval": 10,
            "npoints": npoints,
            "end_time": start_time + npoints * 10 - 10,
            "size": npoints * 4
        }

    @staticmethod
    def get_fina_meta_slim():
        """Get finaMeta data"""
        npoints = 360
        start_time = EmonFinaDataTest.get_time_start_2()
        return {
            "start_time": start_time,
            "interval": 10,
            "npoints": npoints,
            "end_time": start_time + npoints * 10 - 10,
            "size": npoints * 4
        }