"""Constants used for generating random trees.

Copyright © 2017-2018 Wren Powell <wrenp@duck.com>

This file is part of skiddie.

skiddie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

skiddie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with skiddie.  If not, see <http://www.gnu.org/licenses/>.
"""
# Strings that can be used as the values of nodes in the tree. Each list represents a set of values that can be used
# together.
NODE_VALUE_SETS = [
    [
        # German towns and cities.
        "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Stuttgart", "Dortmund", "Essen", "Leipzig", "Bremen",
        "Dresden", "Hanover", "Nuremberg", "Duisburg", "Bochum", "Wuppertal", "Bielefeld", "Bonn", "Mannheim",
        "Augsburg", "Wiesbaden", "Chemnitz", "Kiel", "Aachen", "Halle", "Krefeld", "Rostock", "Kassel", "Hagen",
        "Hammelburg",
    ],
    [
        # Japanese first names.
        "Sasaki", "Senri", "Itoh", "Takano", "Akagi", "Sadow", "Hatanaka", "Yoshimi", "Morine", "Karasu", "Oshima",
        "Dewa", "Ohno", "Tamura", "Nakai", "Asari", "Kanagi", "Nakano", "Uchida", "Imada", "Okamura", "Yasui", "Eto",
        "Ohori", "Sama", "Kawai", "Yajima", "Koide", "Hatsu", "Zayasu",
    ],
    [
        # Elements of the periodic table.
        "Beryllium", "Boron", "Argon", "Scandium", "Vanadium", "Germanium", "Selenium", "Krypton", "Rubidium",
        "Strontium", "Yttrium", "Niobium", "Ruthenium", "Tellurium", "Lanthanum", "Cerium", "Promethium", "Samarium",
        "Europium", "Terbium", "Holmium", "Ytterbium", "Lutetium", "Dubnium", "Hassium", "Nihonium", "Flerovium",
        "Moscovium", "Tennesine", "Oganesson",
    ],
    [

        # Celestial bodies.
        "Deimos", "Phobos", "Ceres", "Pallas", "Vesta", "Hygiea", "Io", "Europa", "Ganymede", "Callisto", "Mimas",
        "Enceladus", "Tethys", "Dione", "Rhea", "Titan", "Hyperion", "Iapetus", "Phoebe", "Miranda", "Ariel", "Umbriel",
        "Titania", "Oberon", "Proteus", "Triton", "Nereid", "Haumea", "Pluto", "Damocloids",
    ],
    [
        # Animal genera.
        "Bos", "Canis", "Capra", "Castor", "Elephas", "Equus", "Felis", "Galago", "Homo", "Hystrix", "Lama", "Lepus",
        "Loris", "Martes", "Meles", "Nasua", "Ochotona", "Ovis", "Pan", "Panthera", "Pedetes", "Phoca", "Pongo",
        "Potus", "Rattus", "Setifer", "Sus", "Tamias", "Tapirus", "Vulpes",
    ],
    [
        # Famous scientists.
        "Einstein", "Darwin", "Newton", "Copernicus", "Galileo", "Curie", "Haber", "Higgs", "Edison", "Tesla",
        "Faraday", "Bohr", "Planck", "Kepler", "Fermi", "Feynman", "Volta", "Kelvin", "Turing", "Thompson", "Ritchie",
        "Kunth", "Hubble", "Franklin", "Meitner", "Hawking", "Pasteur", "Da Vinci", "Bell", "Aristotle",
    ],
    [
        # Constellations.
        "Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Ophiuchus", "Aquila", "Aries", "Cetus", "Cygnus", "Delphinus", "Draco", "Hydra", "Lyra",
        "Orion", "Pegasus", "Ursa", "Canis", "Eridanus", "Lupus", "Perseus", "Corvus", "Hercules",
    ],
    [
        # Greek gods and titans.
        "Aphrodite", "Apollo", "Ares", "Artemis", "Athena", "Demeter", "Dionysus", "Hades", "Hephaestus", "Hera",
        "Hermes", "Hestia", "Poseidon", "Zeus", "Cronus", "Hyperion", "Iapetus", "Phoebe", "Rhea", "Theia", "Atlas",
        "Eos", "Prometheus", "Pallas", "Styx", "Metis", "Leto", "Selene", "Helios", "Dione",
    ],
    [
        # Types of rock.
        "Andesite", "Basalt", "Diorite", "Granite", "Obsidian", "Pumice", "Rhyolite", "Chalk", "Coal", "Flint",
        "Sandstone", "Shale", "Marble", "Schist", "Slate", "Basanite", "Pegmatite", "Trachyte", "Lignite", "Marl",
        "Phosphorite", "Anthracite", "Gneiss", "Mylonite", "Phyllite", "Chert", "Tuff", "Tonalite", "Norite", "Latite",
    ],
    [
        # Types of trees.
        "Ash", "Aspen", "Mahogany", "Beech", "Birch", "Butternut", "Chestnut", "Cottonwood", "Elm", "Fir", "Hawthorn",
        "Hemlock", "Hickory", "Larch", "Maple", "Oak", "Pine", "Cedar", "Spruce", "Sycamore", "Walnut", "Willow",
        "Eucalyptus", "Dogwood", "Sassafras", "Locust", "Hornbeam", "Cherry", "Tulip", "Basswood",
    ]
]
