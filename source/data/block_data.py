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
    OFFICE = auto()
    NECROTECH_LAB = auto() 
    JUNKYARD = auto()
    MUSEUM = auto()
    NIGHTCLUB = auto()
    PUB = auto()
    MALL = auto()
    BANK = auto()
    CINEMA = auto()
    HOTEL = auto()
    RAILWAY_STATION = auto()
    TOWER = auto()

    STREET = auto()
    PARK = auto()
    CEMETERY = auto()
    MONUMENT = auto()
    CARPARK = auto()


BlockProperties = namedtuple(
    'BlockProperties', ['description', 'is_building', 'image_file']
)

BLOCKS = {
    BlockType.FIRE_STATION: BlockProperties("a fire station", True, ResourcePath("blocks/fire_station.bmp").path),
    BlockType.POLICE_DEPARTMENT: BlockProperties("a police department", True, ResourcePath("blocks/police_department.bmp").path),
    BlockType.HOSPITAL: BlockProperties("a hospital", True, ResourcePath("blocks/hospital.bmp").path),
    BlockType.LIBRARY: BlockProperties("a library", True, ResourcePath("blocks/library.bmp").path),
    BlockType.CHURCH: BlockProperties("a church", True, ResourcePath("blocks/church.bmp").path),
    BlockType.WAREHOUSE: BlockProperties("a warehouse", True, ResourcePath("blocks/warehouse.bmp").path),
    BlockType.AUTO_REPAIR: BlockProperties("an auto repair shop", True, ResourcePath("blocks/auto_repair.bmp").path),
    BlockType.FACTORY: BlockProperties("a factory", True, ResourcePath("blocks/factory.bmp").path),
    BlockType.SCHOOL: BlockProperties("a school", True, ResourcePath("blocks/school.bmp").path),
    BlockType.OFFICE: BlockProperties("an office building", True, ResourcePath("blocks/office.bmp").path),
    BlockType.NECROTECH_LAB: BlockProperties("a NecroTech lab", True, ResourcePath("blocks/necrotech_lab.bmp").path),
    BlockType.JUNKYARD: BlockProperties("a junkyard", True, ResourcePath("blocks/junkyard.bmp").path),
    BlockType.MUSEUM: BlockProperties("a museum", True, ResourcePath("blocks/museum.bmp").path),
    BlockType.NIGHTCLUB: BlockProperties("a nightclub", True, ResourcePath("blocks/nightclub.bmp").path),
    BlockType.PUB: BlockProperties("a pub", True, ResourcePath("blocks/pub.bmp").path),
    BlockType.MALL: BlockProperties("a mall", True, ResourcePath("blocks/mall.bmp").path),
    BlockType.BANK: BlockProperties("a bank", True, ResourcePath("blocks/bank.bmp").path),
    BlockType.CINEMA: BlockProperties("a cinema", True, ResourcePath("blocks/cinema.bmp").path),
    BlockType.HOTEL: BlockProperties("a hotel", True, ResourcePath("blocks/hotel.bmp").path),
    BlockType.RAILWAY_STATION: BlockProperties("a railway station", True, ResourcePath("blocks/railway_station.bmp").path),
    BlockType.TOWER: BlockProperties("a towering skyscraper", True, ResourcePath("blocks/tower.bmp").path),

    BlockType.STREET: BlockProperties("a street", False, ResourcePath("blocks/streets.bmp").path),
    BlockType.PARK: BlockProperties("a park", False, ResourcePath("blocks/park.bmp").path),
    BlockType.CEMETERY: BlockProperties("a cemetery", False, ResourcePath("blocks/cemetery.bmp").path),
    BlockType.MONUMENT: BlockProperties("a monument", False, ResourcePath("blocks/monument.bmp").path),
    BlockType.CARPARK: BlockProperties("a carpark", False, ResourcePath("blocks/carpark.bmp").path),
}