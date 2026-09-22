from playersData import pdata
import ba, setting, _ba
from stats import mystats
sett = setting.get_settings_data()

def addtag(node,player):
    profiles=[]
    app = _ba.app
    session_player=player.sessionplayer
    account_id=session_player.get_v1_account_id()
    profiles=session_player.inputdevice.get_player_profiles()
    customtag_=pdata.get_custom()
    customtag=customtag_['customtag']
    roles=pdata.get_roles()
    p_roles=pdata.get_player_roles(account_id)
    tag=None
    col=(0.5,0.5,1) # default color for custom tags
    if account_id in customtag:
        tag=customtag[account_id]
    elif p_roles !=[]:
        for role in roles:
            if role in p_roles:
                tag=roles[role]['tag']
                col=roles[role]['tagcolor']
                break;
    if not profiles:
        profiles = app.config.get('Player Profiles', {})
    if tag:
        Tag(node,tag,col,player,profiles)


def addrank(node,player):
    session_player=player.sessionplayer
    account_id=session_player.get_v1_account_id()
    rank=mystats.getRank(account_id)

    if rank:
        Rank(node,rank)


def addhp(node, spaz):
    def showHP():
        hp = spaz.hitpoints
        if spaz.node.exists():
            HitPoint(owner=node,prefix=str(int(hp)),position=(0,1.75,0),shad = 1.4)
        else:
            spaz.hptimer = None

    spaz.hptimer = ba.Timer(100,ba.Call(showHP),repeat = True, timetype=ba.TimeType.SIM, timeformat=ba.TimeFormat.MILLISECONDS)


def addping(node, spaz):
    """Attaches a smooth 3D ping indicator underneath player feet."""
    if node and node.exists():
        Ping(owner=node, spaz=spaz)


class Ping(object):
    def __init__(self, owner=None, spaz=None):
        self.node = owner
        self.spaz = spaz

        # Smooth position binding via math node (Y offset -0.8 for under feet)
        mnode = ba.newnode('math',
                           owner=self.node,
                           attrs={
                               'input1': (0, -0.8, 0),
                               'operation': 'add'
                           })
        self.node.connectattr('torso_position', mnode, 'input2')

        # Create smooth in-world ping text node
        self.ping_text = ba.newnode('text',
                                    owner=self.node,
                                    attrs={
                                        'text': '...',
                                        'in_world': True,
                                        'shadow': 0.5,
                                        'flatness': 1.0,
                                        'color': (1, 1, 1),
                                        'scale': 0.009,
                                        'h_align': 'center',
                                        'v_align': 'center'
                                    })
        mnode.connectattr('output', self.ping_text, 'position')

        # Periodic timer to update numerical ping value & color
        self.timer = ba.Timer(
            200,
            ba.Call(self._update_ping),
            repeat=True,
            timetype=ba.TimeType.SIM,
            timeformat=ba.TimeFormat.MILLISECONDS
        )

    def _get_ping_color(self, ping_ms: float) -> tuple[float, float, float]:
        if ping_ms < 50:
            return (0.0, 1.0, 0.2)    # Cyan-Green
        elif ping_ms < 100:
            return (0.2, 1.0, 0.0)    # Green
        elif ping_ms < 150:
            return (0.9, 1.0, 0.0)    # Yellow
        elif ping_ms < 200:
            return (1.0, 0.5, 0.0)    # Orange
        else:
            return (1.0, 0.1, 0.1)    # Red

    def _update_ping(self) -> None:
        if not self.node.exists() or not self.spaz or not self.spaz.is_alive():
            self.timer = None
            return

        player = self.spaz.getplayer(ba.Player)
        if player and player.sessionplayer and player.sessionplayer.inputdevice:
            client_id = player.sessionplayer.inputdevice.client_id
            try:
                ping_val = _ba.get_client_ping(client_id)
                if ping_val is not None:
                    self.ping_text.text = f"{ping_val}ms"
                    self.ping_text.color = self._get_ping_color(float(ping_val))
            except Exception:
                pass


class Tag(object):
    def __init__(self, owner=None, tag="something", col=(1, 1, 1), player=None, profiles=None):
        self.node = owner
        self.player = player
        self.profiles = profiles
        self.tag = tag
        mnode = ba.newnode('math',
                           owner=self.node,
                           attrs={
                               'input1': (0, 1.5, 0),
                               'operation': 'add'
                           })
        self.node.connectattr('torso_position', mnode, 'input2')

        if self.check_permissions():
            custom_tag = self.parse_custom_tag()
            tag_text = custom_tag if custom_tag else tag
            self.create_tag_text(tag_text, col, mnode)
        else:
            custom_tag = self.parse_custom_tag()
            tag_text = custom_tag if custom_tag else tag
            self.create_tag_text(tag_text, col, mnode)            

    def check_permissions(self):
        session_player = self.player.sessionplayer
        account_id = session_player.get_v1_account_id()
        roles = pdata.get_roles()
        for role in roles:
            if account_id in roles[role]["ids"]:
                return True
        return False

    def parse_custom_tag(self):
        session_player = self.player.sessionplayer
        account_id = session_player.get_v1_account_id()
        customtag_ = pdata.get_custom()
        customtag = customtag_['customtag']
        tags = customtag.get(account_id)

        if tags is not None:
            return self.process_escape_sequences(tags)
        if sett["EnablePlayerProfilesTag"]:
            for p in self.profiles:
                if '/tag' in p:
                    try:
                        tagg = p.split('/tag', 1)[1].strip()
                        return self.process_escape_sequences(tagg)
                    except IndexError:
                        pass

        return self.process_escape_sequences(self.tag)

    def process_escape_sequences(self, tag):
        if '\\' in tag:
            tag = tag.replace('\\d', ('\ue048')) \
                     .replace('\\c', ('\ue043')) \
                     .replace('\\h', ('\ue049')) \
                     .replace('\\s', ('\ue046')) \
                     .replace('\\n', ('\ue04b')) \
                     .replace('\\f', ('\ue04f')) \
                     .replace('\\g', ('\ue027')) \
                     .replace('\\i', ('\ue03a')) \
                     .replace('\\m', ('\ue04d')) \
                     .replace('\\t', ('\ue01f')) \
                     .replace('\\bs', ('\ue01e')) \
                     .replace('\\j', ('\ue010')) \
                     .replace('\\e', ('\ue045')) \
                     .replace('\\l', ('\ue047')) \
                     .replace('\\a', ('\ue020')) \
                     .replace('\\b', ('\ue00c'))
        return tag

    def create_tag_text(self, tag_text, col, mnode):
        self.tag_text = ba.newnode('text',
                                    owner=self.node,
                                    attrs={
                                        'text': tag_text,
                                        'in_world': True,
                                        'shadow': 1.0,
                                        'flatness': 1.0,
                                        'color': tuple(col),
                                        'scale': 0.01,
                                        'h_align': 'center'
                                    })
        mnode.connectattr('output', self.tag_text, 'position')

        if sett["enableTagAnimation"]:
            ba.animate_array(node=self.tag_text, attr='color', size=3, keys={
                0.2: (2, 0, 2),
                0.4: (2, 2, 0),
                0.6: (0, 2, 2),
                0.8: (2, 0, 2),
                1.0: (1, 1, 0),
                1.2: (0, 1, 1),
                1.4: (1, 0, 1)
            }, loop=True)


class Rank(object):
    def __init__(self, owner=None, rank=99):
        self.node = owner
        mnode = ba.newnode('math',
                           owner=self.node,
                           attrs={
                               'input1': (0, 1.2, 0),
                               'operation': 'add'
                           })
        self.node.connectattr('torso_position', mnode, 'input2')
        if (rank == 1):
            rank = '\ue043' + "#"+str(rank) +'\ue043'
        elif (rank == 2):
            rank = '\ue048' + "#"+str(rank) +'\ue048'
        elif (rank == 3):
            rank = '\ue01f' + "#"+str(rank) +'\ue01f'
        else:
            rank = '\ue047' + "#"+str(rank)

        self.rank_text = ba.newnode('text',
                                    owner=self.node,
                                    attrs={
                                        'text': rank,
                                        'in_world': True,
                                        'shadow': 1.0,
                                        'flatness': 1.0,
                                        'color': (1,1,1),
                                        'scale': 0.01,
                                        'h_align': 'center'
                                    })
        mnode.connectattr('output', self.rank_text, 'position')


class HitPoint(object):
    def __init__(self, position=(0, 1.5, 0), owner=None, prefix='0', shad=1.2):
        self.position = position
        self.node = owner
        m = ba.newnode('math', owner=self.node, attrs={'input1': self.position, 'operation': 'add'})
        self.node.connectattr('torso_position', m, 'input2')
        prefix = int(prefix) / 10
        preFix = u"\ue047" + str(prefix) + u"\ue047"
        self._Text = ba.newnode('text',
                                owner=self.node,
                                attrs={
                                    'text': preFix,
                                    'in_world': True,
                                    'shadow': shad,
                                    'flatness': 1.0,
                                    'color': (1,1,1) if int(prefix) >= 20 else (1.0,0.2,0.2),
                                    'scale': 0.01,
                                    'h_align': 'center'})
        m.connectattr('output', self._Text, 'position')
        def a():
            self._Text.delete()
            m.delete()
        self.timer = ba.Timer(100, ba.Call(a), timetype=ba.TimeType.SIM, timeformat=ba.TimeFormat.MILLISECONDS)