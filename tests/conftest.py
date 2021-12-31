import pytest


@pytest.fixture
def client():
    from src import app

    app.app.config['TESTING'] = True

    app.db.engine.execute('DROP TABLE IF EXISTS `rooms`;')

    app.db.engine.execute('''CREATE TABLE `rooms` (
  `room_id` int NOT NULL AUTO_INCREMENT,
  `capacity` int NOT NULL,
  `price` float NOT NULL,
  `floor` int NOT NULL,
  PRIMARY KEY (`room_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;''')

    app.db.engine.execute(
        '''INSERT INTO `rooms` VALUES
        (1,5,100.0,1),(2,20,200.0,1),(3,20,200.0,2),
        (4,50,300.0,1),(5,5,100.0,4);''')

    return app.app.test_client()
