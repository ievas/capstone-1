
from models import User, Level, Badge, Streak, UserBadge
from app import db

db.drop_all()
db.create_all()

# beauty - add a profile pic, pioneer - earn first 10 points, prodigy - earn 30 points, mastermind - complete a level with no mistakes

beauty = Badge(name='beauty', icon_url="/static/images/woman.png")
pioneer = Badge(name='pioneer', icon_url="/static/images/goal.png")
prodigy = Badge(name='prodigy', icon_url="/static/images/mind.png")
mastermind = Badge(name='mastermind', icon_url="/static/images/idea.png")

level_1 = Level(name='Level 1')
level_2 = Level(name='Level 2')
level_3 = Level(name='Level 3')

db.session.add_all([level_1, level_2, level_3])
db.session.add_all([beauty, pioneer, prodigy, mastermind])
db.session.commit()