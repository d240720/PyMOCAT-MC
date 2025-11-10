"""
Set object class to one of these satellite types after explosion or collision

Maps object classes to fragment classes:
- 'Payload Fragmentation Debris' = 3
- 'Rocket Fragmentation Debris' = 7
- 'Other Debris' = 10
- 'Unknown' = 11

Args:
    objclass_org: original object class (1-11)

Returns:
    satellite_type: fragment object class (3, 7, 9, 10, or 11)

Object class definitions:
    1 = 'Payload'
    2 = 'Payload Mission Related Object'
    3 = 'Payload Fragmentation Debris'
    4 = 'Payload Debris'
    5 = 'Rocket Body'
    6 = 'Rocket Mission Related Object'
    7 = 'Rocket Fragmentation Debris'
    8 = 'Rocket Debris'
    9 = 'Debris' (new)
    10 = 'Other Debris'
    11 = 'Unknown' or []
"""

def filter_objclass_fragments_int(objclass_org):
    """
    Set object class for fragments based on parent object class

    Args:
        objclass_org: original object class (1-11)

    Returns:
        satellite_type: fragment object class (3, 7, 9, 10, or 11)
    """

    if objclass_org < 4.5:
        satellite_type = 3  # 'Payload Fragmentation Debris'
    elif objclass_org < 8.5:
        satellite_type = 7  # 'Rocket Fragmentation Debris'
    elif objclass_org == 9:
        satellite_type = 9  # 'Debris'
    elif objclass_org == 10:
        satellite_type = 10  # 'Other Debris'
    elif objclass_org == 11:
        satellite_type = 11  # 'Unknown' or []
    else:
        raise ValueError(f'objclass {objclass_org} did not match any \
            of the pre-determined options. '
                        'Please review this function to assign object \
                            class to one of these satellite types: '
                        '[\'Payload Fragmentation Debris\', \'Rocket \
                            Fragmentation Debris\', \'Debris\', '
                        '\'Other Debris\' or \'Unknown\']')

    return satellite_type
