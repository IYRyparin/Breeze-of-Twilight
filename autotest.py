from src.parser import ConfigurationStandalone


def testout(file: str = "./grammar/basic.bot"):
    with open(file, "r", encoding="utf-8") as f:
        stand = ConfigurationStandalone(f.read())
        print()
        print("CONFIG_ID:", stand.CONFIGURATION_ID)
        print("CONFIG_READONLY:", stand.CONFIGURATION_READONLY)
        print("CONFIG_VERSION:", stand.CONFIGURATION_VERSION)
        print("CONFIG_ENCODE:", stand.CONFIGURATION_ENCODE)
        print("LOAD_STRING:", stand.dictionary["load_string"].value)
        print("RUN-COMP:", stand.dictionary["run-comp"].value)
        print("PANE:", stand.dictionary["pane"].value)
        print("LOAD_LIMIT:", stand.dictionary["load_limit"].limit_value_list)
        print("LOAD_REGULAR:", stand.dictionary["load_regular"].limit_value_list)
        print("REGEX_VALUE:", stand.dictionary["load_regular"].value)


if __name__ == "__main__":
    testout()
