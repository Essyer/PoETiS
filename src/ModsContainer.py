import re
import xml.etree.ElementTree as ElementTree

DEFAULT_FILTER_PATH = "filters/mods.xml"
CONFIG_PATH = "config.xml"


class ModsContainer:
    mods = {}

    @staticmethod
    def get_mod_key(mod_text: str) -> str:
        return re.sub(r'(\d+(\.\d+)?)', 'x', mod_text)

    @staticmethod
    def get_mod_value(mod_text: str) -> float:
        # Find floats
        mods = re.findall(r'(\d+\.\d+)', mod_text)
        value = 0
        if mods:
            value = sum(map(float, mods))/len(mods)
        else:
            # No floats, find ints
            mods = re.findall(r'(\d+)', mod_text)
            if mods:  # Just to be sure mod has any number, if it doesn't we can't process it
                value = sum(map(float, mods)) / len(mods)

        return value

    def process_totals(self, filter_dict: dict, cat: ElementTree.Element) -> None:
        # Currently not used
        # For each mod in item we would have to scan all total mods to check if it is a part of some total mod
        # Creates additional dictionary entry if 'totals' node exists.
        # Entry is a dictionary with mod text as key. Values are dictionaries with mod minimal value
        # and list of mods text that account for given total mod, e.g.:
        # filter_dict = {
        #   accessory{
        #       'x% to cold resistance': 20.0
        #       ...
        #       'totals': {
        #           'x% to all elemental resistances': {
        #               'value': 50.0
        #               'mods': ['x% to cold resistance', 'x% to fire resistance', 'x% to lightning resistance']
        #           }
        #       }
        #   }
        # }
        if cat.tag not in filter_dict:
            filter_dict[cat.tag] = {}
        totals_cat = cat.find('totals')
        if totals_cat:
            totals_cat = list(totals_cat)
            filter_dict[cat.tag]['totals'] = {self.get_mod_key(total.find('value_text').text): {
                'value': self.get_mod_value(total.find('value_text').text),
                'mods': [subtotal.text for subtotal in total.findall('mod')]}
                for total in totals_cat}

    @staticmethod
    def load_mods_config(xml_path: str) -> None:
        filter_dict = {}
        root = ElementTree.parse(xml_path).getroot()
        category1 = list(root)  # weapon, accessory, armour...
        for cat1 in category1:
            mods1 = cat1.findall('mod')
            if mods1:
                mods1 = list(mods1)
                filter_dict[cat1.tag] = {
                    ModsContainer.get_mod_key(mod.text): ModsContainer.get_mod_value(mod.text) for mod in mods1
                }
                # Creates dictionary entry, e.g:
                # filter_dict{
                #   'x to dexterity': 30.0
                #   ...
                # }

            # process_totals(filter_dict, cat1)

            category2 = list(cat1)  # bow, claw, helmet, ring...
            for cat2 in category2:
                if cat2.tag == 'mods' or cat2.tag == 'totals':
                    continue
                mods2 = list(cat2)
                if mods2:
                    if cat1.tag not in filter_dict:
                        filter_dict[cat1.tag] = {}
                    filter_dict[cat1.tag][cat2.tag] = {
                        ModsContainer.get_mod_key(mod.text): ModsContainer.get_mod_value(mod.text)
                        for mod in mods2 if mod.tag != 'totals'
                    }
                # process_totals(filter_dict, cat2)
        ModsContainer.mods = filter_dict


# List of all item types from https://pathofexile.gamepedia.com/Public_stash_tab_API
# and item bases from https://pathofexile.gamepedia.com/Equipment
item_bases = {
    'accessory': {
        'amulet': ['Coral Amulet', 'Paula Amulet', 'Amber Amulet', 'Jade Amulet', 'Lapis Amulet', 'Gold Amulet',
                   'Agate Amulet', 'Citrine Amulet', 'Turquoise Amulet', 'Onyx Amulet', 'Marble Amulet',
                   'Blue Pearl Amulet',
                   'Ashscale Talisman', 'Avian Twins Talisman', 'Black Maw Talisman', 'Bonespire Talisman',
                   'Breakrib Talisman', 'Chrysalis Talisman', 'Clutching Talisman', 'Deadhand Talisman',
                   'Deep One Talisman', 'Fangjaw Talisman', 'Greatwolf Talisman', 'Hexclaw Talisman', 'Horned Talisman',
                   'Lone Antler Talisman', 'Longtooth Talisman', 'Mandible Talisman', 'Monkey Paw Talisman',
                   'Monkey Twins Talisman', 'Primal Skull Talisman', 'Rot Head Talisman', 'Rotfeather Talisman',
                   'Spinefuse Talisman', 'Splitnewt Talisman', 'Three Hands Talisman', 'Three Rat Talisman',
                   'Undying Flesh Talisman', 'Wereclaw Talisman', 'Writhing Talisman'],
        'belt': ['Chain Belt', 'Rustic Sash', 'Stygian Vise', 'Heavy Belt', 'Leather Belt', 'Cloth Belt',
                 'Studded Belt', 'Vanguard Belt', 'Crystal Belt'],
        'ring': ['Breach Ring', 'Coral Ring', 'Iron Ring', 'Paula Ring', 'Unset Ring', 'Sapphire Ring', 'Topaz Ring',
                 'Ruby Ring', 'Diamond Ring', 'Gold Ring', 'Moonstone Ring', 'Two-Stone Ring', 'Amethyst Ring',
                 'Prismatic Ring', 'Cerulean Ring', 'Opal Ring', 'Steel Ring', 'Vermillion Ring']
    },
    'armour': {
        'boots': ['Iron Greaves', 'Steel Greaves', 'Plated Greaves', 'Reinforced Greaves', 'Antique Greaves',
                  'Ancient Greaves', 'Goliath Greaves', 'Vaal Greaves', 'Titan Greaves',
                  'Rawhide Boots', 'Goathide Boots', 'Deerskin Boots', 'Nubuck Boots', 'Eelskin Boots',
                  'Sharkskin Boots', 'Shagreen Boots', 'Stealth Boots', 'Slink Boots',
                  'Wool Shoes', 'Velvet Slippers', 'Silk Slippers', 'Scholar Boots', 'Satin Slippers',
                  'Samite Slippers', 'Conjured Boots', 'Arcanist Slippers', 'Sorcerer Boots',
                  'Leatherscale Boots', 'Ironscale Boots', 'Bronzescale Boots', 'Steelscale Boots',
                  'Serpentscale Boots', 'Wyrmscale Boots', 'Hydrascale Boots', 'Dragonscale Boots', 'Teo-Toned Boots',
                  'Chain Boots', 'Ringmail Boots', 'Mesh Boots', 'Riveted Boots', 'Zealot Boots', 'Soldier Boots',
                  'Legion Boots', 'Crusader Boots',
                  'Wrapped Boots', 'Strapped Boots', 'Clasped Boots', 'Shackled Boots', 'Trapper Boots', 'Ambush Boots',
                  'Carnal Boots', 'Assassin\'s Boots', 'Murder Boots'],
        'chest': ['Plate Vest', 'Chestplate', 'Copper Plate', 'War Plate', 'Full Plate', 'Arena Plate', 'Lordly Plate',
                  'Bronze Plate', 'Battle Plate', 'Sun Plate', 'Colosseum Plate', 'Majestic Plate', 'Golden Plate',
                  'Crusader Plate', 'Astral Plate', 'Gladiator Plate', 'Glorious Plate',
                  'Shabby Jerkin', 'Strapped Leather', 'Buckskin Tunic', 'Wild Leather', 'Full Leather', 'Sun Leather',
                  'Thief\'s Garb', 'Eelskin Tunic', 'Frontier Leather', 'Glorious Leather', 'Coronal Leather'
                                                                                            'Cutthroat\'s Garb',
                  'Sharkskin Tunic', 'Destiny Leather', 'Exquisite Leather', 'Zodiac Leather',
                  'Assassin\'s Garb',
                  'Simple Robe', 'Silken Vest', 'Scholar\'s Robe', 'Silken Garb', 'Mage\'s Vestment', 'Silk Robe',
                  'Cabalist Regalia', 'Sage\'s Robe', 'Silken Wrap', 'Conjurer\'s Vestment', 'Spidersilk Robe',
                  'Destroyer Regalia', 'Savant\'s Robe', 'Necromancer Silks', 'Occultist\'s Vestment', 'Widowsilk Robe',
                  'Vaal Regalia',
                  'Scale Vest', 'Light Brigandine', 'Scale Doublet', 'Infantry Brigandine', 'Full Scale Armour',
                  'Soldier\'s Brigandine', 'Field Lamellar', 'Wyrmscale Doublet', 'Hussar Brigandine', 'Full Wyrmscale',
                  'Commander\'s Brigandine', 'Battle Lamellar', 'Dragonscale Doublet', 'Desert Brigandine',
                  'Full Dragonscale', 'General\'s Brigandine', 'Triumphant Lamellar',
                  'Chainmail Vest', 'Chainmail Tunic', 'Ringmail Coat', 'Chainmail Doublet', 'Full Ringmail',
                  'Full Chainmail', 'Holy Chainmail', 'Latticed Ringmail', 'Crusader Chainmail', 'Ornate Ringmail',
                  'Chain Hauberk', 'Devout Chainmail', 'Loricated Ringmail', 'Conquest Chainmail', 'Elegant Ringmail',
                  'Saint\'s Hauberk', 'Saintly Chainmail',
                  'Padded Vest', 'Oiled Vest', 'Padded Jacket', 'Oiled Coat', 'Scarlet Raiment', 'Waxed Garb',
                  'Bone Armour', 'Quilted Jacket', 'Sleek Coat', 'Crimson Raiment', 'Lacquered Garb', 'Crypt Armour',
                  'Sentinel Jacket', 'Varnished Coat', 'Blood Rainment', 'Sadist Garb', 'Carnal Armour',
                  'Sacrificial Garb'],
        'gloves': ['Iron Gauntlets', 'Plated Gauntlets', 'Bronze Gauntlets', 'Steel Gauntlets', 'Antique Gauntlets',
                   'Ancient Gauntlets', 'Goliath Gauntlets', 'Vaal Gauntlets', 'Titan Gauntlets', 'Spiked Gloves',
                   'Rawhide Gloves', 'Goathide Gloves', 'Deerskin Gloves', 'Nubuck Gloves', 'Eelskin Gloves',
                   'Sharkskin Gloves', 'Shagreen Gloves', 'Stealth Gloves', 'Gripped Gloves', 'Slink Gloves',
                   'Wool Gloves', 'Velvet Gloves', 'Silk Gloves', 'Embroidered Gloves', 'Satin Gloves', 'Samite Gloves',
                   'Conjured Gloves', 'Arcanist Gloves', 'Sorcerer Gloves', 'Fingerless Silk Gloves',
                   'Fishscale Gauntlets', 'Ironscale Gauntlets', 'Bronzescale Gauntlets', 'Steelscale Gauntlets',
                   'Serpentscale Gauntlets', 'Wyrmscale Gauntlets', 'Hydrascale Gauntlets', 'Dragonscale Gauntlets',
                   'Chain Gloves', 'Ringmail Gloves', 'Mesh Gloves', 'Rivetet Gloves', 'Zealot Gloves',
                   'Soldier Gloves', 'Legion Gloves', 'Crusader Gloves',
                   'Wrapped Mitts', 'Strapped Mitts', 'Clasped Mitts', 'Trapper Mitts', 'Ambush Mitts', 'Carnal Mitts',
                   'Assassin\'s Mitts', 'Murder Mitts'],
        'helmet': ['Iron Hat', 'Cone Helmet', 'Barbute Helmet', 'Close Helmet', 'Gladiator Helmet', 'Reaver Helmet',
                   'Siege Helmet', 'Samite Helmet', 'Ezomyte Burgonet', 'Royal Burgonet', 'Eternal Burgonet',
                   'Leather Cap', 'Tricorne', 'Leather Hood', 'Wolf Pelt', 'Hunter Hood', 'Noble Tricorne',
                   'Ursine Pelt', 'Silken Hood', 'Sinner Tricorne', 'Lion Pelt',
                   'Vine Circlet', 'Iron Circlet', 'Torture Cage', 'Tribal Circlet', 'Bone Circlet', 'Lunaris Circlet',
                   'Steel Circlet', 'Necromancer Circlet', 'Mind Cage', 'Hubris Circlet',
                   'Battered Helm', 'Sallet', 'Visored Sallet', 'Gilded Sallet', 'Secutor Helm', 'Fencer Helm',
                   'Lacquered Helm', 'Fluted Bascinet', 'Pig-Faced Bascinet', 'Nightmare Bascinet',
                   'Rusted Coif', 'Soldier Helmet', 'Great Helmet', 'Crusader Helmet', 'Aventail Helmet',
                   'Zealot Helmet', 'Great Crown', 'Magistrate Crown', 'Prophet Crown', 'Praetor Crown', 'Bone Helmet',
                   'Scare Mask', 'Plague Mask', 'Iron Mask', 'Festival Mask', 'Golden Mask', 'Raven Mask',
                   'Callous Mask', 'Regicide Mask', 'Harlequin Mask', 'Vaal Mask', 'Deicide Mask'],
        'shield': ['Splintered Tower Shield', 'Corroded Tower Shield', 'Rawhide Tower Shield', 'Cedar Tower Shield',
                   'Copper Tower Shield', 'Reinforced Tower Shield', 'Painted Tower Shield', 'Buckskin Tower Shield',
                   'Mahogany Tower Shield', 'Bronze Tower Shield', 'Girded Tower Shield', 'Crested Tower Shield',
                   'Shagreen Tower Shield', 'Ebony Tower Shield', 'Ezomyte Tower Shield', 'Colossal Tower Shield',
                   'Pinnacle Tower Shield',
                   'Goathide Buckler', 'Pine Buckler', 'Painted Buckler', 'Hammered Buckler', 'War Buckler',
                   'Gilded Buckler', 'Oak Buckler', 'Enameled Buckler', 'Corrugated Buckler', 'Battle Buckler',
                   'Golden Buckler', 'Ironwood Buckler', 'Lacquered Buckler', 'Vaal Buckler', 'Crusader Buckler',
                   'Imperial Buckler',
                   'Twig Spirit Shield', 'Yew Spirit Shield', 'Bone Spirit Shield', 'Tarnished Spirit Shield',
                   'Jingling Spirit Shield', 'Brass Spirit Shield', 'Walnut Spirit Shield', 'Ivory Spirit Shield',
                   'Ancient Spirit Shield', 'Chiming Spirit Shield', 'Thorium Spirit Shield', 'Lacewood Spirit Shield',
                   'Fossilised Spirit Shield', 'Vaal Spirit Shield', 'Harmonic Spirit Shield', 'Titanium Spirit Shield',
                   'Rotted Round Shield', 'Fir Round Shield', 'Studded Round Shield', 'Scarlet Round Shield',
                   'Splendid Round Shield', 'Maple Round Shield', 'Spiked Round Shield', 'Crimson Round Shield',
                   'Baroque Round Shield', 'Teak Round Shield', 'Spiny Round Shield', 'Cardinal Round Shield',
                   'Elegant Round Shield',
                   'Plank Kite Shield', 'Linden Kite Shield', 'Reinforced Kite Shield', 'Layered Kite Shield',
                   'Ceremonial Kite Shield', 'Etched Kite Shield', 'Steel Kite Shield', 'Laminated Kite Shield',
                   'Angelic Kite Shield', 'Branded Kite Shield', 'Champion Kite Shield', 'Mosaic Kite Shield',
                   'Archon Kite Shield',
                   'Spiked Bundle', 'Driftwood Spiked Shield', 'Alloyed Spiked Shield', 'Burnished Spiked Shield',
                   'Ornate Spiked Shield', 'Redwood Spiked Shield', 'Compound Spiked Shield', 'Polished Spiked Shield',
                   'Sovereign Spiked Shield', 'Alder Spiked Shield', 'Ezomyte Spiked Shield', 'Mirrored Spiked Shield',
                   'Supreme Spiked Shield'],
        'quiver': ['Two-Point Arrow Quiver', 'Serrated Arrow Quiver', 'Sharktooth Arrow Quiver', 'Blunt Arrow Quiver',
                   'Fire Arrow Quiver', 'Broadhead Arrow Quiver', 'Penetrating Arrow Quiver', 'Ornate Quiver',
                   'Spike-Point Arrow Quiver'],

    },
    'weapon': {
        'bow': ['Crude Bow', 'Short Bow', 'Long Bow', 'Composite Bow', 'Recurve Bow', 'Bone Bow', 'Royal Bow',
                'Death Bow', 'Grove Bow', 'Reflex Bow', 'Decurve Bow', 'Compound Bow', 'Sniper Bow', 'Ivory Bow',
                'Highborn Bow', 'Decimation Bow', 'Thicket Bow', 'Steelwood Bow', 'Citadel Bow', 'Ranger Bow',
                'Assassin Bow', 'Spine Bow', 'Imperial Bow', 'Harbinger Bow', 'Maraketh Bow'],
        'claw': ['Nailed Fist', 'Sharktooth Claw', 'Awl', 'Cat\'s Paw', 'Blinder', 'Timeworn Claw', 'Sparkling Claw',
                 'Fright Claw', 'Double Claw', 'Thresher Claw', 'Gouger', 'Tiger\'s Paw', 'Gut Ripper',
                 'Prehistoric Claw', 'Noble Claw', 'Eagle Claw', 'Twin Claw', 'Great White Claw', 'Throat Stabber',
                 'Hellion\'s Paw', 'Eye Gouger', 'Vaal Claw', 'Imperial Claw', 'Terror Claw', 'Gemini Claw'],
        'dagger': ['Glass Shank', 'Skinning Knife', 'Stiletto', 'Flaying Knife', 'Prong Dagger', 'Poignard', 'Trisula',
                   'Gutting Knife', 'Ambusher', 'Sai', 'Carving Knife', 'Boot Knife', 'Copper Kris', 'Skean',
                   'Imp Dagger', 'Butcher Knife', 'Boot Blade', 'Royal Skean', 'Fiend Dagger', 'Slaughter Knife',
                   'Ezomyte Dagger', 'Platinum Kris', 'Imperial Skean', 'Demon Dagger'],

        'sceptre': ['Driftwood Sceptre', 'Darkwood Sceptre', 'Bronze Sceptre', 'Quartz Sceptre', 'Iron Sceptre',
                    'Ochre Sceptre', 'Ritual Sceptre', 'Shadow Sceptre', 'Grinning Sceptre', 'Horned Sceptre',
                    'Sekhem', 'Crystal Sceptre', 'Lead Sceptre', 'Blood Sceptre', 'Royal Sceptre', 'Abyssal Sceptre',
                    'Stag Sceptre', 'Karui Sceptre', 'Tyrant\'s Sceptre', 'Opal Sceptre', 'Platinum Sceptre',
                    'Vaal Sceptre', 'Carnal Sceptre', 'Void Sceptre', 'Sambar Sceptre'],
        'staff': ['Gnarled Branch', 'Primitive Staff', 'Long Staff', 'Royal Staff', 'Crescent Staff', 'Woodful Staff',
                  'Quarterstaff', 'Highborn Staff', 'Moon Staff', 'Primordial Staff', 'Lathi', 'Imperial Staff',
                  'Eclipse Staff', 'Iron Staff', 'Coiled Staff', 'Vile Staff', 'Military Staff', 'Serpentine Staff',
                  'Foul Staff', 'Ezomyte Staff', 'Maelström Staff', 'Judgement Staff'],
        'wand': ['Driftwood Wand', 'Goat\'s Horn', 'Carved Wand', 'Quartz Wand', 'Spiraled Wand', 'Sage Wand',
                 'Pagan Wand', 'Faun\'s Horn', 'Engraved Wand', 'Crystal Wand', 'Serpent Wand', 'Omen Wand',
                 'Heathen Wand', 'Demon\'s Horn', 'Imbued Wand', 'Opal Wand', 'Tornado Wand', 'Prophecy Wand',
                 'Profane Wand', 'Convoking Wand'],
        'oneaxe': ['Rusted Hatchet', 'Jade Hatchet', 'Boarding Axe', 'Cleaver', 'Broad Axe', 'Arming Axe',
                   'Decorative Axe', 'Spectral Axe', 'Etched Hatchet', 'Jasper Axe', 'Tomahawk', 'Wrist Chopper',
                   'War Axe', 'Chest Splitter', 'Ceremonial Axe', 'Wraith Axe', 'Engraved Hatchet', 'Karui Axe',
                   'Siege Axe', 'Reaver Axe', 'Butcher Axe', 'Vaal Hatchet', 'Royal Axe', 'Infernal Axe',
                   'Runic Hatchet'],
        'twoaxe': ['Stone Axe', 'Jade Chopper', 'Woodsplitter', 'Poleaxe', 'Double Axe', 'Gilded Axe', 'Shadow Axe',
                   'Dagger Axe', 'Jasper Chopper', 'Timber Axe', 'Headsman Axe', 'Labrys', 'Noble Axe', 'Abyssal Axe',
                   'Karui Chopper', 'Talon Axe', 'Sundering Axe', 'Ezomyte Axe', 'Vaal Axe', 'Despot Axe', 'Void Axe',
                   'Fleshripper'],
        'onemace': ['Driftwood Club', 'Tribal Club', 'Spiked Club', 'Stone Hammer', 'War Hammer', 'Bladed Mace',
                    'Ceremonial Mace', 'Dream Mace', 'Wyrm Mace', 'Petrified Club', 'Barbed Club', 'Rock Breaker',
                    'Battle Hammer', 'Flanged Mace', 'Ornate Mace', 'Phantom Mace', 'Dragon Mace', 'Ancestral Club',
                    'Tenderizer', 'Gavel', 'Legion Hammer', 'Pernarch', 'Auric Mace', 'Nightmare Mace',
                    'Behemoth Mace'],
        'twomace': ['Driftwood Maul', 'Tribal Maul', 'Mallet', 'Sledgehammer', 'Jagged Maul', 'Brass Maul',
                    'Fright Maul', 'Morning Star', 'Totemic Maul', 'Great Mallet', 'Steelhead', 'Spiny Maul',
                    'Plated Maul', 'Dread Maul', 'Solar Maul', 'Karui Maul', 'Colossus Mallet', 'Piledriver',
                    'Meatgrinder', 'Imperial Maul', 'Terror Maul', 'Coronal Maul'],
        'onesword': ['Rusted Sword', 'Copper Sword', 'Sabre', 'Broad Sword', 'War Sword', 'Ancient Sword',
                     'Elegant Sword', 'Dusk Blade', 'Hook Sword', 'Variscite Blade', 'Cutlass', 'Baselard',
                     'Battle Sword', 'Elder Sword', 'Graceful Sword', 'Twilight Blade', 'Grappler', 'Gemstone Sword',
                     'Corsair Sword', 'Gladius', 'Legion Sword', 'Vaal Blade', 'Eternal Sword', 'Midnight Blade',
                     'Tiger Hook', 'Rusted Spike', 'Whalebone Rapier', 'Battered Foil', 'Basket Rapier', 'Jagged Foil',
                     'Antique Rapier', 'Elegant Foil', 'Thorn Rapier', 'Smallsword', 'Wyrmbone Rapier',
                     'Burnished Foil', 'Estoc', 'Serrated Foil', 'Primeval Rapier', 'Fancy Foil', 'Apex Rapier',
                     'Courtesan Sword', 'Dragonbone Rapier', 'Tempered Foil', 'Pecoraro', 'Spiraled Foil',
                     'Vaal Rapier', 'Jewelled Foil', 'Harpy Rapier', 'Dragoon Sword'],

        'twosword': ['Corroded Blade', 'Longsword', 'Bastard Sword', 'Two-Handed Sword', 'Etched Greatsword',
                     'Ornate Sword', 'Spectral Sword', 'Curved Blade', 'Butcher Sword', 'Footman Sword',
                     'Highland Blade', 'Engraved Greatsword', 'Tiger Sword', 'Wraith Sword', 'Lithe Blade',
                     'Headman\'s Sword', 'Reaver Sword', 'Ezomyte Blade', 'Vaal Greatsword', 'Lion Sword',
                     'Infernal Sword', 'Exquisite Blade'],
    }
}
