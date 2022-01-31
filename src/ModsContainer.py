import os.path
import platform
import re
import xml.etree.ElementTree as ElementTree

if platform.system().lower() == 'windows':
    PROJECT_ROOT = "."  # os.path redirects to TEMP
else:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__ + "/.."))

FILTER_DIR = PROJECT_ROOT + "/filters/"
DEFAULT_FILTER_PATH = FILTER_DIR + "mods.xml"
CONFIG_PATH = PROJECT_ROOT + "/config.xml"


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


# List of all item categories from https://pathofexile.fandom.com/wiki/Public_stash_tab_API under "category" section
# and item bases from https://pathofexile.fandom.com/wiki/Equipment
# Tool will compare to API result only item names like 'Silk Slippers', 'armour' and 'boots' in this dict are only
# for convenience of future edits. GGG's public stash api provides "extended" information for each item in stash,
# for example "extended":{"category":"accessories","subcategories":["ring"],"prefixes":1,"suffixes":3}
# private API does not return this additional information, that's why we need all item bases listed below.
item_bases = {
    'jewels': {
        'base': ['Cobalt Jewel', 'Crimson Jewel', 'Viridian Jewel'],
        'abyss': ['Ghastly Eye Jewel', 'Hypnotic Eye Jewel', 'Murderous Eye Jewel', 'Searching Eye Jewel'],
        'cluster': ['Small Cluster Jewel', 'Medium Cluster Jewel', 'Large Cluster Jewel']
    },
    'accessories': {
        'amulet': ['Coral Amulet', 'Paua Amulet', 'Amber Amulet', 'Jade Amulet', 'Lapis Amulet', 'Gold Amulet',
                   'Agate Amulet', 'Citrine Amulet', 'Turquoise Amulet', 'Onyx Amulet', 'Simplex Amulet',
                   'Astrolabe Amulet', 'Marble Amulet', 'Seaglass Amulet', 'Blue Pearl Amulet',

                   'Ashscale Talisman', 'Avian Twins Talisman', 'Black Maw Talisman', 'Bonespire Talisman',
                   'Breakrib Talisman', 'Chrysalis Talisman', 'Clutching Talisman', 'Deadhand Talisman',
                   'Deep One Talisman', 'Fangjaw Talisman', 'Greatwolf Talisman', 'Hexclaw Talisman', 'Horned Talisman',
                   'Lone Antler Talisman', 'Longtooth Talisman', 'Mandible Talisman', 'Monkey Paw Talisman',
                   'Monkey Twins Talisman', 'Primal Skull Talisman', 'Rot Head Talisman', 'Rotfeather Talisman',
                   'Spinefuse Talisman', 'Splitnewt Talisman', 'Three Hands Talisman', 'Three Rat Talisman',
                   'Undying Flesh Talisman', 'Wereclaw Talisman', 'Writhing Talisman'],

        'belt': ['Chain Belt', 'Rustic Sash', 'Stygian Vise', 'Heavy Belt', 'Leather Belt', 'Cloth Belt',
                 'Studded Belt', 'Micro-Distillery Belt', 'Mechalarm Belt', 'Vanguard Belt', 'Crystal Belt'],

        'ring': ['Breach Ring', 'Coral Ring', 'Iron Ring', 'Paula Ring', 'Unset Ring', 'Sapphire Ring', 'Topaz Ring',
                 'Ruby Ring', 'Diamond Ring', 'Gold Ring', 'Moonstone Ring', 'Two-Stone Ring', 'Cogwork Ring',
                 'Geodesic Ring', 'Amethyst Ring', 'Prismatic Ring', 'Iolite Ring', 'Cerulean Ring', 'Opal Ring',
                 'Steel Ring', 'Vermillion Ring']
    },
    'armour': {
        'boots': ['Iron Greaves', 'Steel Greaves', 'Basemetal Treads', 'Plated Greaves', 'Reinforced Greaves',
                  'Antique Greaves', 'Ancient Greaves', 'Darksteel Treads', 'Goliath Greaves', 'Vaal Greaves',
                  'Titan Greaves', 'Brimstone Treads',

                  'Rawhide Boots', 'Goathide Boots', 'Cloudwhisper Boots', 'Deerskin Boots', 'Nubuck Boots',
                  'Eelskin Boots', 'Sharkskin Boots', 'Windbreak Boots', 'Shagreen Boots', 'Stealth Boots',
                  'Slink Boots', 'Stormrider Boots',

                  'Wool Shoes', 'Velvet Slippers', 'Duskwalk Slippers', 'Silk Slippers', 'Scholar Boots',
                  'Satin Slippers', 'Samite Slippers', 'Nightwind Slippers', 'Conjurer Boots', 'Arcanist Slippers',
                  'Sorcerer Boots', 'Dreamquest Slippers',

                  'Leatherscale Boots', 'Ironscale Boots', 'Bronzescale Boots', 'Steelscale Boots',
                  'Serpentscale Boots', 'Wyrmscale Boots', 'Hydrascale Boots', 'Dragonscale Boots', 'Teo-Toned Boots',

                  'Chain Boots', 'Ringmail Boots', 'Mesh Boots', 'Riveted Boots', 'Zealot Boots', 'Soldier Boots',
                  'Legion Boots', 'Crusader Boots',

                  'Wrapped Boots', 'Strapped Boots', 'Clasped Boots', 'Shackled Boots', 'Trapper Boots', 'Ambush Boots',
                  'Carnal Boots', 'Assassin\'s Boots', 'Murder Boots', 'Fugitive Boots'],

        'chest': ['Plate Vest', 'Chestplate', 'Copper Plate', 'War Plate', 'Full Plate', 'Arena Plate', 'Lordly Plate',
                  'Bronze Plate', 'Battle Plate', 'Sun Plate', 'Colosseum Plate', 'Majestic Plate', 'Golden Plate',
                  'Crusader Plate', 'Astral Plate', 'Gladiator Plate', 'Glorious Plate',

                  'Shabby Jerkin', 'Strapped Leather', 'Buckskin Tunic', 'Wild Leather', 'Full Leather', 'Sun Leather',
                  'Thief\'s Garb', 'Eelskin Tunic', 'Frontier Leather', 'Glorious Leather', 'Coronal Leather',
                  'Cutthroat\'s Garb', 'Sharkskin Tunic', 'Destiny Leather', 'Exquisite Leather', 'Zodiac Leather',
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

                  'Grasping Mail', 'Sacrificial Garb'],

        'gloves': ['Iron Gauntlets', 'Taxing Gauntlets', 'Plated Gauntlets', 'Bronze Gauntlets', 'Steel Gauntlets',
                   'Antique Gauntlets', 'Gruelling Gauntlets', 'Ancient Gauntlets', 'Goliath Gauntlets',
                   'Vaal Gauntlets', 'Titan Gauntlets', 'Debilitation Gauntlets', 'Spiked Gloves',

                   'Rawhide Gloves', 'Goathide Gloves', 'Gauche Gloves', 'Deerskin Gloves', 'Nubuck Gloves',
                   'Eelskin Gloves', 'Southswing Gloves', 'Sharkskin Gloves', 'Shagreen Gloves', 'Stealth Gloves',
                   'Gripped Gloves', 'Sinistral Gloves', 'Slink Gloves',

                   'Wool Gloves', 'Leyline Gloves', 'Velvet Gloves', 'Silk Gloves', 'Embroidered Gloves',
                   'Aetherwind Gloves', 'Satin Gloves', 'Samite Gloves', 'Conjurer Gloves', 'Arcanist Gloves',
                   'Sorcerer Gloves', 'Fingerless Silk Gloves', 'Nexus Gloves',

                   'Fishscale Gauntlets', 'Ironscale Gauntlets', 'Bronzescale Gauntlets', 'Steelscale Gauntlets',
                   'Serpentscale Gauntlets', 'Wyrmscale Gauntlets', 'Hydrascale Gauntlets', 'Dragonscale Gauntlets',

                   'Chain Gloves', 'Ringmail Gloves', 'Mesh Gloves', 'Riveted Gloves', 'Zealot Gloves',
                   'Soldier Gloves', 'Legion Gloves', 'Crusader Gloves', 'Apothecary\'s Gloves',

                   'Wrapped Mitts', 'Strapped Mitts', 'Clasped Mitts', 'Trapper Mitts', 'Ambush Mitts', 'Carnal Mitts',
                   'Assassin\'s Mitts', 'Murder Mitts'],

        'helmet': ['Iron Hat', 'Cone Helmet', 'Barbute Helmet', 'Close Helmet', 'Gladiator Helmet', 'Reaver Helmet',
                   'Siege Helmet', 'Samnite Helmet', 'Ezomyte Burgonet', 'Royal Burgonet', 'Eternal Burgonet',

                   'Leather Cap', 'Tricorne', 'Leather Hood', 'Wolf Pelt', 'Hunter Hood', 'Noble Tricorne',
                   'Ursine Pelt', 'Silken Hood', 'Sinner Tricorne', 'Lion Pelt',

                   'Vine Circlet', 'Iron Circlet', 'Torture Cage', 'Tribal Circlet', 'Bone Circlet', 'Lunaris Circlet',
                   'Steel Circlet', 'Necromancer Circlet', 'Solaris Circlet', 'Mind Cage', 'Hubris Circlet',

                   'Battered Helm', 'Sallet', 'Sorrow Mask', 'Visored Sallet', 'Gilded Sallet', 'Secutor Helm',
                   'Fencer Helm', 'Atonement Mask', 'Lacquered Helm', 'Fluted Bascinet', 'Pig-Faced Bascinet',
                   'Nightmare Bascinet', 'Penitent Mask',

                   'Rusted Coif', 'Soldier Helmet', 'Imp Crown', 'Great Helmet', 'Crusader Helmet', 'Aventail Helmet',
                   'Zealot Helmet', 'Demon Crown', 'Great Crown', 'Magistrate Crown', 'Prophet Crown', 'Praetor Crown',
                   'Bone Helmet', 'Archdemon Crown',

                   'Scare Mask', 'Plague Mask', 'Gale Crown', 'Iron Mask', 'Festival Mask', 'Golden Mask', 'Raven Mask',
                   'Callous Mask', 'Winter Crown', 'Regicide Mask', 'Harlequin Mask', 'Vaal Mask', 'Deicide Mask',
                   'Blizzard Crown'],

        'shield': ['Splintered Tower Shield', 'Corroded Tower Shield', 'Rawhide Tower Shield', 'Cedar Tower Shield',
                   'Copper Tower Shield', 'Exothermic Tower Shield', 'Reinforced Tower Shield', 'Painted Tower Shield',
                   'Buckskin Tower Shield', 'Mahogany Tower Shield', 'Bronze Tower Shield', 'Magmatic Tower Shield',
                   'Girded Tower Shield', 'Crested Tower Shield', 'Shagreen Tower Shield', 'Ebony Tower Shield',
                   'Ezomyte Tower Shield', 'Colossal Tower Shield', 'Heat-attuned Tower Shield',
                   'Pinnacle Tower Shield',

                   'Goathide Buckler', 'Pine Buckler', 'Painted Buckler', 'Hammered Buckler', 'War Buckler',
                   'Endothermic Buckler', 'Gilded Buckler', 'Oak Buckler', 'Enameled Buckler', 'Corrugated Buckler',
                   'Battle Buckler', 'Polar Buckler', 'Golden Buckler', 'Ironwood Buckler', 'Lacquered Buckler',
                   'Vaal Buckler', 'Crusader Buckler', 'Imperial Buckler', 'Cold-attuned Buckler',

                   'Twig Spirit Shield', 'Yew Spirit Shield', 'Bone Spirit Shield', 'Tarnished Spirit Shield',
                   'Jingling Spirit Shield', 'Exhausting Spirit Shield', 'Brass Spirit Shield', 'Walnut Spirit Shield',
                   'Ivory Spirit Shield', 'Ancient Spirit Shield', 'Chiming Spirit Shield', 'Subsuming Spirit Shield',
                   'Thorium Spirit Shield', 'Lacewood Spirit Shield', 'Fossilised Spirit Shield', 'Vaal Spirit Shield',
                   'Harmonic Spirit Shield', 'Titanium Spirit Shield', 'Transfer-attuned Spirit Shield'
                                                                                                                         
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
                   'Spike-Point Arrow Quiver', 'Artillery Quiver'],
    },
    'weapons': {
        'bow': ['Crude Bow', 'Short Bow', 'Long Bow', 'Composite Bow', 'Recurve Bow', 'Bone Bow', 'Royal Bow',
                'Hedron Bow', 'Death Bow', 'Grove Bow', 'Reflex Bow', 'Decurve Bow', 'Compound Bow', 'Sniper Bow',
                'Ivory Bow', 'Foundry Bow', 'Highborn Bow', 'Decimation Bow', 'Thicket Bow', 'Steelwood Bow',
                'Citadel Bow', 'Ranger Bow', 'Assassin Bow', 'Spine Bow', 'Imperial Bow', 'Harbinger Bow',
                'Solarine Bow', 'Maraketh Bow'],

        'claw': ['Nailed Fist', 'Sharktooth Claw', 'Awl', 'Cat\'s Paw', 'Blinder', 'Timeworn Claw', 'Shadow Fangs',
                 'Sparkling Claw', 'Fright Claw', 'Double Claw', 'Thresher Claw', 'Gouger', 'Tiger\'s Paw',
                 'Gut Ripper', 'Prehistoric Claw', 'Malign Fangs', 'Noble Claw', 'Eagle Claw', 'Twin Claw',
                 'Great White Claw', 'Throat Stabber', 'Hellion\'s Paw', 'Eye Gouger', 'Vaal Claw', 'Imperial Claw',
                 'Terror Claw', 'Void Fangs', 'Gemini Claw'],

        'dagger': ['Glass Shank', 'Skinning Knife', 'Stiletto', 'Flaying Knife', 'Hollowpoint Dagger', 'Prong Dagger',
                   'Poignard', 'Pressurised Dagger', 'Trisula', 'Gutting Knife', 'Ambusher', 'Pneumatic Dagger', 'Sai',

                   'Carving Knife', 'Boot Knife', 'Copper Kris', 'Skean', 'Flickerflame Blade',
                   'Imp Dagger', 'Butcher Knife', 'Boot Blade', 'Golden Kris', 'Flashfire Blade', 'Royal Skean',
                   'Fiend Dagger', 'Slaughter Knife', 'Ezomyte Dagger', 'Platinum Kris', 'Imperial Skean',
                   'Demon Dagger', 'Infernal Blade'],

        'sceptre': ['Driftwood Sceptre', 'Darkwood Sceptre', 'Bronze Sceptre', 'Quartz Sceptre', 'Iron Sceptre',
                    'Ochre Sceptre', 'Ritual Sceptre', 'Oscillating Sceptre', 'Shadow Sceptre', 'Grinning Sceptre',
                    'Horned Sceptre', 'Sekhem', 'Crystal Sceptre', 'Lead Sceptre', 'Blood Sceptre', 'Royal Sceptre',
                    'Stabilising Sceptre', 'Abyssal Sceptre', 'Stag Sceptre', 'Karui Sceptre', 'Tyrant\'s Sceptre',
                    'Opal Sceptre', 'Platinum Sceptre', 'Vaal Sceptre', 'Carnal Sceptre', 'Void Sceptre',
                    'Alternating Sceptre', 'Sambar Sceptre'],

        'staff': ['Gnarled Branch', 'Primitive Staff', 'Long Staff', 'Royal Staff', 'Transformer Staff',
                  'Crescent Staff', 'Woodful Staff', 'Quarterstaff', 'Reciprocation Staff', 'Highborn Staff',
                  'Moon Staff', 'Primordial Staff', 'Lathi', 'Imperial Staff', 'Battery Staff', 'Eclipse Staff',

                  'Iron Staff', 'Coiled Staff', 'Capacity Rod', 'Vile Staff', 'Military Staff', 'Serpentine Staff',
                  'Potentiality Rod', 'Foul Staff', 'Ezomyte Staff', 'Maelström Staff', 'Judgement Staff',
                  'Eventuality Rod'],

        'wand': ['Driftwood Wand', 'Goat\'s Horn', 'Carved Wand', 'Quartz Wand', 'Spiraled Wand', 'Assembler Wand',
                 'Sage Wand', 'Pagan Wand', 'Faun\'s Horn', 'Engraved Wand', 'Crystal Wand', 'Serpent Wand',
                 'Congregator Wand', 'Omen Wand', 'Heathen Wand', 'Demon\'s Horn', 'Imbued Wand', 'Opal Wand',
                 'Tornado Wand', 'Prophecy Wand', 'Accumulator Wand', 'Profane Wand', 'Convoking Wand'],

        'oneaxe': ['Rusted Hatchet', 'Jade Hatchet', 'Boarding Axe', 'Cleaver', 'Broad Axe', 'Arming Axe',
                   'Decorative Axe', 'Maltreatment Axe', 'Spectral Axe', 'Etched Hatchet', 'Jasper Axe',
                   'Tomahawk', 'Wrist Chopper', 'War Axe', 'Chest Splitter', 'Disapprobation Axe', 'Ceremonial Axe',
                   'Wraith Axe', 'Engraved Hatchet', 'Karui Axe', 'Siege Axe', 'Reaver Axe', 'Butcher Axe',
                   'Vaal Hatchet', 'Royal Axe', 'Infernal Axe', 'Psychotic Axe', 'Runic Hatchet'],

        'twoaxe': ['Stone Axe', 'Jade Chopper', 'Woodsplitter', 'Poleaxe', 'Double Axe', 'Gilded Axe', 'Prime Cleaver',
                   'Shadow Axe', 'Dagger Axe', 'Jasper Chopper', 'Timber Axe', 'Headsman Axe', 'Labrys',
                   'Honed Cleaver', 'Noble Axe', 'Abyssal Axe', 'Karui Chopper', 'Talon Axe', 'Sundering Axe',
                   'Ezomyte Axe', 'Vaal Axe', 'Despot Axe', 'Void Axe', 'Apex Cleaver', 'Fleshripper'],

        'onemace': ['Driftwood Club', 'Tribal Club', 'Spiked Club', 'Stone Hammer', 'War Hammer', 'Bladed Mace',
                    'Ceremonial Mace', 'Flare Mace', 'Dream Mace', 'Wyrm Mace', 'Petrified Club', 'Barbed Club',
                    'Rock Breaker', 'Battle Hammer', 'Flanged Mace', 'Crack Mace', 'Ornate Mace', 'Phantom Mace',
                    'Dragon Mace', 'Ancestral Club', 'Tenderizer', 'Gavel', 'Legion Hammer', 'Pernarch', 'Auric Mace',
                    'Nightmare Mace', 'Behemoth Mace', 'Boom Mace'],

        'twomace': ['Driftwood Maul', 'Tribal Maul', 'Mallet', 'Sledgehammer', 'Jagged Maul', 'Brass Maul',
                    'Blunt Force Condenser', 'Fright Maul', 'Morning Star', 'Totemic Maul', 'Great Mallet', 'Steelhead',
                    'Spiny Maul', 'Crushing Force Magnifier', 'Plated Maul', 'Dread Maul', 'Solar Maul', 'Karui Maul',
                    'Colossus Mallet', 'Piledriver', 'Meatgrinder', 'Imperial Maul', 'Terror Maul', 'Coronal Maul',
                    'Impact Force Propagator'],

        'onesword': ['Rusted Spike', 'Rusted Sword', 'Copper Sword', 'Whalebone Rapier', 'Sabre', 'Battered Foil',
                     'Broad Sword', 'Basket Rapier', 'War Sword', 'Jagged Foil', 'Ancient Sword', 'Antique Rapier',
                     'Elegant Sword', 'Elegant Foil', 'Fickle Spiritblade', 'Dusk Blade', 'Hook Sword', 'Thorn Rapier',
                     'Variscite Blade', 'Smallsword', 'Wyrmbone Rapier', 'Cutlass', 'Burnished Foil', 'Baselard',
                     'Estoc', 'Battle Sword', 'Serrated Foil', 'Elder Sword', 'Primeval Rapier',
                     'Capricious Spiritblade', 'Graceful Sword', 'Fancy Foil', 'Twilight Blade', 'Apex Rapier',
                     'Grappler', 'Gemstone Sword', 'Courtesan Sword', 'Corsair Sword', 'Dragonbone Rapier', 'Gladius',
                     'Tempered Foil', 'Legion Sword', 'Pecoraro', 'Spiraled Foil', 'Vaal Blade', 'Eternal Sword',
                     'Vaal Rapier', 'Jewelled Foil', 'Midnight Blade', 'Anarchic Spiritblade', 'Harpy Rapier',
                     'Tiger Hook', 'Dragoon Sword'],

        'twosword': ['Corroded Blade', 'Longsword', 'Bastard Sword', 'Two-Handed Sword', 'Etched Greatsword',
                     'Ornate Sword', 'Rebuking Blade', 'Spectral Sword', 'Curved Blade', 'Butcher Sword',
                     'Footman Sword', 'Highland Blade', 'Engraved Greatsword', 'Blasting Blade', 'Tiger Sword',
                     'Wraith Sword', 'Lithe Blade', 'Headman\'s Sword', 'Reaver Sword', 'Ezomyte Blade',
                     'Vaal Greatsword', 'Lion Sword', 'Infernal Sword', 'Banishing Blade', 'Exquisite Blade'],
    }
}

# For chaos recipe
one_handed = ['shield', 'claw', 'dagger', 'sceptre', 'wand', 'oneaxe', 'onemace', 'onesword']
two_handed = ['bow', 'staff', 'twoaxe', 'twomace', 'twosword']
items_categories = ['weapon', 'weapon', 'helmet', 'chest', 'gloves', 'boots', 'belt', 'amulet', 'ring', 'ring']
items_categories_filter = {
    'chest': "Body Armours",
    'helmet': "Helmets",
    'gloves': "Gloves",
    'boots': "Boots",
    'weapon': 'weapon',  # needs special handling
    'ring': "Rings",
    'amulet': "Amulets",
    'belt': "Belts"
}
