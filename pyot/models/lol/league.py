from .__core__ import PyotCore, PyotStatic
from typing import List, Iterator

# PYOT STATIC OBJECTS

class MiniSeriesData(PyotStatic):
    target: int
    wins: int
    losses: int
    progress: str


class LeagueEntryData(PyotStatic):
    summoner_id: str
    summoner_name: str
    league_points: int
    rank: str
    wins: int
    losses: int
    veteran: bool
    inactive: bool
    fresh_blood: bool
    hot_streak: bool
    mini_series: MiniSeriesData

    @property
    def summoner(self) -> "Summoner":
        from .summoner import Summoner
        return Summoner(id=self.summoner_id, name=self.summoner_name, platform=self.platform)


class SummonerLeagueEntryData(LeagueEntryData):
    league_id: str
    queue: str
    tier: str

    class Meta(LeagueEntryData.Meta):
        renamed = {"queue_type": "queue"}

    @property
    def league(self) -> "League":
        return League(id=self.league_id, platform=self.platform)


# PYOT CORE OBJECTS

class League(PyotCore):
    tier: str
    id: str
    queue: str
    name: str
    entries: List[LeagueEntryData]
    
    class Meta(PyotCore.Meta):
        rules = {"league_v4_league_by_league_id": ["id"]}
        renamed = {"league_id": "id"}

    def __init__(self, id: str = None, platform: str = None):
        self._lazy_set(locals())


class ApexLeague(League):
    queue: str
    id: str
    
    class Meta(League.Meta):
        queue_list = ["RANKED_SOLO_5x5", "RANKED_FLEX_SR"]
    
    def __init__(self, queue: str = None, platform: str = None):
        self._lazy_set(locals())
    
    async def _clean(self):
        if self.queue not in self._meta.queue_list:
            raise AttributeError(f"Invalid 'queue' attribute, '{self.queue}' was given")

    @property
    def league(self) -> "League":
        return League(id=self.id, platform=self.platform)


class ChallengerLeague(ApexLeague):
    
    class Meta(ApexLeague.Meta):
        rules = {"league_v4_challenger_league": ["queue"]}


class GrandmasterLeague(ApexLeague):
    
    class Meta(ApexLeague.Meta):
        rules = {"league_v4_grandmaster_league": ["queue"]}


class MasterLeague(ApexLeague):
    
    class Meta(ApexLeague.Meta):
        rules = {"league_v4_master_league": ["queue"]}


class SummonerLeague(PyotCore):
    summoner_id: str
    entries: List[SummonerLeagueEntryData]

    class Meta(PyotCore.Meta):
        rules = {"league_v4_summoner_entries": ["summoner_id"]}

    def __init__(self, summoner_id: str = None, platform: str = None):
        self._lazy_set(locals())
    
    def __getitem__(self, item):
        if not isinstance(item, int):
            return super().__getitem__(item)
        return self.entries[item]
    
    def __iter__(self) -> Iterator[SummonerLeagueEntryData]:
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)

    def _transform(self, data):
        new_data = {}
        new_data["entries"] = data
        return new_data
    
    @property
    def summoner(self) -> "Summoner":
        from .summoner import Summoner
        return Summoner(id=self.summoner_id, platform=self.platform)


class DivisionLeague(SummonerLeague):
    queue: str
    division: str
    tier: str

    class Meta(SummonerLeague.Meta):
        rules = {"league_v4_entries_by_division": ["queue", "tier", "division"]}
        queue_list = ["RANKED_SOLO_5x5", "RANKED_FLEX_SR"]
        division_list = ["I", "II", "III", "IV"]
        tier_list = ["DIAMOND", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
        allow_query = True

    def __init__(self, queue: str = None, division: str = None, tier: str = None, platform: str = None):
        self._lazy_set(locals())

    def query(self, page: int = None):
        '''Add query parameters to the object.'''
        if page == 0: raise AttributeError("Invalid 'page' attribute, it should be greater than 0")
        self._meta.query = self._parse_camel(locals())
        return self

    async def _clean(self):
        if self.queue not in self._meta.queue_list:
            raise AttributeError(f"Invalid 'queue' attribute, '{self.queue}' was given")
        if self.division not in self._meta.division_list:
            raise AttributeError(f"Invalid 'division' attribute, '{self.division}' was given")
        if self.tier not in self._meta.tier_list:
            raise AttributeError(f"Invalid 'tier' attribute, '{self.tier}' was given")

    @property
    def summoner(self) -> AttributeError:
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute 'summoner'")
