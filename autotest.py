from src.parser import ConfigurationStandalone


def testout(file: str = "./grammar/basic.bot"):
    with open(file, "r") as f:
        stand = ConfigurationStandalone(f.read())
        print("\n")
        print(stand.CONFIGURATION_ID)
        print(stand.CONFIGURATION_READONLY)
        print(stand.CONFIGURATION_VERSION)
        print(stand.CONFIGURATION_ENCODE)
        print(stand._dictionary)
        print(stand._dictionary['example_partition']._value)
    f.close()
