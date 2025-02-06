# block_data.py

from enum import Enum, auto
from collections import namedtuple

from data.path import ResourcePath


class BlockType(Enum):
    FIRE_STATION = auto()
    POLICE_DEPARTMENT = auto()
    HOSPITAL = auto()
    LIBRARY = auto()
    CHURCH = auto()
    WAREHOUSE = auto()
    AUTO_REPAIR = auto()
    FACTORY = auto()
    SCHOOL = auto()
    NECROTECH_LAB = auto() 
    JUNKYARD = auto()
    MUSEUM = auto()
    NIGHTCLUB = auto()
    PUB = auto()
    MALL = auto()

    STREET = auto()
    PARK = auto()
    CEMETERY = auto()
    MONUMENT = auto()
    CARPARK = auto()


BlockProperties = namedtuple(
    'BlockProperties', ['description', 'is_building', 'image_file']
)

BLOCKS = {
    BlockType.FIRE_STATION: BlockProperties("a fire station", True, ResourcePath("assets/fire_station.bmp").path),
    BlockType.POLICE_DEPARTMENT: BlockProperties("a police department", True, ResourcePath("assets/police_department.bmp").path),
    BlockType.HOSPITAL: BlockProperties("a hospital", True, ResourcePath("assets/hospital.bmp").path),
    BlockType.LIBRARY: BlockProperties("a library", True, ResourcePath("assets/library.bmp").path),
    BlockType.CHURCH: BlockProperties("a church", True, ResourcePath("assets/church.bmp").path),
    BlockType.WAREHOUSE: BlockProperties("a warehouse", True, ResourcePath("assets/warehouse.bmp").path),
    BlockType.AUTO_REPAIR: BlockProperties("an auto repair shop", True, ResourcePath("assets/auto_repair.bmp").path),
    BlockType.FACTORY: BlockProperties("a factory", True, ResourcePath("assets/factory.bmp").path),
    BlockType.SCHOOL: BlockProperties("a school", True, ResourcePath("assets/school.bmp").path),
    BlockType.NECROTECH_LAB: BlockProperties("a NecroTech lab", True, ResourcePath("assets/necrotech_lab.bmp").path),
    BlockType.JUNKYARD: BlockProperties("a junkyard", True, ResourcePath("assets/junkyard.bmp").path),
    BlockType.MUSEUM: BlockProperties("a museum", True, ResourcePath("assets/museum.bmp").path),
    BlockType.NIGHTCLUB: BlockProperties("a nightclub", True, ResourcePath("assets/nightclub.bmp").path),
    BlockType.PUB: BlockProperties("a pub", True, ResourcePath("assets/pub.bmp").path),
    BlockType.MALL: BlockProperties("a mall", True, ResourcePath("assets/mall.bmp").path),

    BlockType.STREET: BlockProperties("a street", False, ResourcePath("assets/streets.bmp").path),
    BlockType.PARK: BlockProperties("a park", False, ResourcePath("assets/park.bmp").path),
    BlockType.CEMETERY: BlockProperties("a cemetery", False, ResourcePath("assets/cemetery.bmp").path),
    BlockType.MONUMENT: BlockProperties("a monument", False, ResourcePath("assets/monument.bmp").path),
    BlockType.CARPARK: BlockProperties("a carpark", False, ResourcePath("assets/carpark.bmp").path),
}