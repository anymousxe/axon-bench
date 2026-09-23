"""AXE v1.1.1: disjoint, revisioned task banks with executable references."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

from .coding_bank import ROWS as CODE_ROWS
from .reasoning_bank import ROWS as REASON_ROWS

CATEGORIES = ("general", "coding", "reasoning")
DIFFICULTIES = ("easy", "medium", "hard", "expert")
TASK_REVISION = "2026-09-23-depth-1"


@dataclass(frozen=True)
class Task:
    prompt: str
    answer: str
    category: str
    pro: bool = False
    kind: str = "exact"
    code_checks: tuple[str, ...] = field(default=(), repr=False)
    aliases: tuple[str, ...] = ()
    test_call: str = ""
    id: str = ""
    difficulty: str = "medium"
    reference: str = ""
    test_cases: tuple = field(default=(), repr=False)
    solution_name: str = ""


# References identify the domain rule or primary source supporting the key.
# Source-bound questions are deliberately closed-world, not trivia lookups.
_GENERAL_ROWS = [
    ("stable-isotope", "Carbon-14 and nitrogen-14 have the same mass number but different atomic numbers. What is the nuclear-chemistry term for this relationship?", "isobars", "easy", False, "IUPAC Gold Book, isobars: nuclides of equal mass number; https://goldbook.iupac.org"),
    ("map-contours", "On a topographic map, contour lines form closed loops with inward-pointing hachures. Does the innermost loop represent a hill or a depression?", "depression", "easy", False, "USGS topographic map symbols: hachured contours indicate depressions; https://pubs.usgs.gov/gip/TopographicMapSymbols/"),
    ("grammar-mood", "In the English clause 'If I were taller', what grammatical mood is illustrated by 'were'?", "subjunctive", "easy", False, "Irrealis/subjunctive were; accepted key uses traditional mood terminology."),
    ("unit-frequency", "What is the SI derived unit for frequency, expressed using its full unit name?", "hertz", "easy", False, "BIPM SI Brochure table of derived units; https://www.bipm.org/en/publications/si-brochure"),
    ("isotope-decay", "A nucleus undergoes one alpha decay followed by two beta-minus decays. Compared with its starting atomic number Z, what is its final atomic number, expressed in terms of Z?", "Z", "medium", False, "Alpha changes Z by -2; each beta-minus changes Z by +1."),
    ("rock-contact", "A limestone body is heated by a nearby intrusion without melting. Which metamorphic rock normally forms from the limestone?", "marble", "medium", False, "Calcite recrystallization of limestone produces marble; USGS metamorphic rock classification."),
    ("phloem-ring", "A narrow ring of bark is removed from a tree while the xylem remains intact. Which vascular tissue responsible for translocating photosynthates has primarily been interrupted?", "phloem", "medium", False, "Phloem lies outside vascular cambium; xylem transports water."),
    ("art-print", "In printmaking, a design is cut below the surface of a metal plate; ink retained in the grooves is transferred under pressure. Name the printmaking family, not one specific cutting technique.", "intaglio", "medium", False, "Metropolitan Museum, intaglio printing; https://www.metmuseum.org/about-the-met/collection-areas/drawings-and-prints/materials-and-techniques/printmaking"),
    ("music-relative", "In common-practice notation, what is the relative minor of E-flat major? Write the tonic letter, accidental if needed, and 'minor'.", "C minor", "medium", False, "Relative minor starts on scale degree six, sharing three flats."),
    ("language-case", "A noun marks the indirect recipient in the canonical grammatical roles nominative=subject and accusative=direct object. Which case conventionally marks this recipient?", "dative", "medium", False, "Traditional nominative-accusative case terminology."),
    ("econ-stock", "GDP is measured over a period, whereas wealth is measured at a point in time. In the stock-flow distinction, which is wealth?", "stock", "medium", False, "UN System of National Accounts stock/flow definitions."),
    ("ecology-succession", "A new lava surface lacks soil. Ecological colonization begins there. Is this primary or secondary succession?", "primary succession", "medium", False, "Primary succession begins without developed soil; secondary retains soil."),
    ("geometry-projection", "Which named cylindrical map projection represents rhumb lines as straight lines but greatly enlarges high-latitude areas?", "Mercator", "medium", False, "USGS Snyder, Map Projections—A Working Manual, Mercator properties; https://pubs.usgs.gov/pp/1395/report.pdf"),
    ("poetry-line", "What is the standard English literary term for an unrhymed line of iambic pentameter?", "blank verse", "medium", False, "Poetry Foundation glossary, blank verse."),
    ("chem-oxidation", "In the ion permanganate, MnO4-, oxygen has oxidation state -2. Give the oxidation state of manganese as a signed integer.", "+7", "medium", False, "x+4(-2)=-1, hence x=+7."),
    ("physics-wave", "Light crosses from vacuum into glass with refractive index greater than one. Which of these is unchanged: speed, wavelength, frequency?", "frequency", "medium", False, "Boundary temporal continuity preserves frequency; v=f lambda."),
    ("genetics-inheritance", "In human mitochondrial inheritance, which parent ordinarily transmits mitochondrial DNA to offspring? Answer 'mother' or 'father'.", "mother", "medium", False, "NHGRI mitochondrial DNA factsheet: maternal inheritance; https://www.genome.gov/genetics-glossary/Mitochondrial-DNA"),
    ("archive-provenance", "An archive preserves records according to the organization that created them rather than mixing records by subject. Name this archival principle in English.", "provenance", "medium", False, "Society of American Archivists Dictionary: principle of provenance."),
    ("eclipse-node", "A solar eclipse requires new Moon and proximity to which intersections of the Moon's orbital plane with the ecliptic? Give the plural noun.", "nodes", "medium", False, "NASA eclipse geometry: eclipses occur near orbital nodes."),
    ("optics-image", "A thin converging lens receives an object located between the lens and its focal point. Is the image real or virtual?", "virtual", "medium", False, "Thin lens equation yields negative image distance when 0<d_o<f."),
    ("statistics-design", "Researchers randomly assign schools, not individual pupils, to an educational intervention. What is the randomization unit?", "school", "medium", False, "Cluster randomized design: assignment unit is school, observation unit may be pupil."),
    ("sediment-grading", "In a normally graded sedimentary bed, grain size decreases from base to top. Does finding coarse grains above fine grains in an otherwise normally graded bed indicate upright or overturned orientation?", "overturned", "medium", False, "Normal grading fines upward; reversed observed orientation is overturned."),
    ("rhetoric-part", "In 'all hands on deck', hands stands for sailors. What is the specific figure of speech in which a part stands for the whole?", "synecdoche", "medium", False, "Part-for-whole synecdoche, distinguished here from broad metonymy."),
    ("astronomy-redshift", "A spectral line emitted at 500 nm is observed at 550 nm. Using z=(observed-emitted)/emitted, give its redshift as a decimal.", "0.1", "medium", False, "Definition of cosmological/spectroscopic redshift: 50/500=0.1."),
    ("gibbs-spontaneity", "At fixed temperature and pressure, a reaction has negative enthalpy change and negative entropy change. According to delta G=delta H-T delta S, is spontaneity favored by lower or higher temperature?", "lower", "hard", False, "Negative entropy adds a positive T-dependent contribution to free energy."),
    ("dna-template", "A DNA template is written 3'-TACGGA-5'. Give the RNA transcribed from it in the 5' to 3' direction, using only letters.", "AUGCCU", "hard", False, "RNA complement pairs T-A,A-U,C-G,G-C and is antiparallel."),
    ("chromatography-retention", "For a chromatographic peak with retention time 12 minutes and dead time 3 minutes, the retention factor is k=(tR-tM)/tM. Give k.", "3", "hard", False, "IUPAC retention factor definition: (12-3)/3."),
    ("music-transposition", "A B-flat clarinet plays written C5. What sounding pitch results? Use scientific pitch notation with 'b' for flat.", "Bb4", "hard", False, "B-flat clarinet sounds a major second below written pitch."),
    ("latin-soundlaw", "Latin pater and English father illustrate the Proto-Indo-European voiceless stop p becoming Germanic f. Name the sound law, giving only the possessive surname plus 'law'.", "Grimm's law", "hard", False, "First Germanic consonant shift, Grimm's law."),
    ("equilibrium-pressure", "For N2(g)+3H2(g) reversible 2NH3(g), increasing pressure at constant temperature by decreasing volume shifts equilibrium toward which named product/reactant?", "ammonia", "hard", False, "Le Chatelier: four gas moles become two; favors NH3."),
    ("geomorph-oxbow", "A river cuts through the neck of a meander, abandoning the old curved channel. What type of lake can occupy the abandoned channel?", "oxbow lake", "hard", False, "USGS fluvial geomorphology: meander cutoff forms oxbow."),
    ("manuscript-recto", "In conventional Western codicology, the front side of a leaf is recto. What is the back side called?", "verso", "hard", False, "Codicological recto/verso terminology."),
    ("electrochem-anode", "In a galvanic cell delivering current, oxidation occurs at which electrode: anode or cathode?", "anode", "hard", False, "IUPAC electrode definitions: oxidation at anode for both galvanic and electrolytic cells."),
    ("evolution-homology", "Bat wing bones and human arm bones derive from the same ancestral tetrapod forelimb despite different functions. Are these structures homologous or analogous?", "homologous", "hard", False, "Homology is common ancestry, not function identity."),
    ("phase-triple", "How many independent intensive degrees of freedom does a one-component system have where three phases coexist in equilibrium? Use Gibbs F=C-P+2.", "0", "hard", False, "Gibbs phase rule: 1-3+2=0."),
    ("phonetics-vot", "The English consonants /p/ and /b/ are both bilabial stops. Which laryngeal feature conventionally distinguishes their phonemic descriptions?", "voicing", "hard", False, "IPA /p/ voiceless, /b/ voiced bilabial plosive."),
    ("immunology-class", "Which immunoglobulin class is the principal antibody class in secretions such as tears and breast milk? Give its standard three-character abbreviation.", "IgA", "hard", False, "NCBI Immunobiology: secretory IgA at mucosal surfaces."),
    ("geology-dike", "A tabular igneous intrusion cuts across bedding rather than lying parallel to it. What is it called?", "dike", "hard", False, "USGS glossary: discordant tabular intrusion=dike; concordant=sill."),
    ("bibliography-anonymous", "A source policy says use organization as author if no personal author exists; use title only if neither exists. A report has no named person, an issuing organization 'Cedar Institute', and title 'Water'. Under this policy, what is its author field?", "Cedar Institute", "hard", False, "Closed-world source policy explicitly gives organization precedence over title."),
    ("statistics-confounding", "A study finds coffee associated with lung cancer; smoking affects both coffee consumption and cancer risk and is not on a causal path from coffee. What is smoking's role in this relationship?", "confounder", "hard", False, "A common cause of exposure and outcome is a confounder."),
    ("economics-opportunity", "A workshop can produce either 6 tables or 18 chairs with the same resources and has a linear production frontier. What is the opportunity cost of one table, in chairs?", "3", "hard", False, "18/6 chairs per table under stated linear frontier."),
    ("meter-hemiola", "A musical passage groups six equal pulses as three groups of two against an underlying two groups of three. What is this 3:2 rhythmic device called?", "hemiola", "hard", False, "Standard music-theory definition of hemiola."),
    ("crystal-system", "A crystal unit cell has a=b=c and alpha=beta=gamma=90 degrees. Which crystal system is this?", "cubic", "hard", False, "IUCr crystal systems: cubic metric constraints."),
    ("library-subject", "A catalog rule assigns one heading to the subject occupying most pages; ties use alphabetically first heading. A book covers Botany on 40 pages, Ecology on 40, and Geology on 20. What heading is assigned?", "Botany", "hard", False, "Closed-world rule: Botany/Ecology tie; Botany alphabetically precedes Ecology."),
    ("spectroscopy-mutual", "For a centrosymmetric molecule under the electric-dipole approximation, can the same fundamental vibrational normal mode be both infrared-active and Raman-active? Answer yes or no.", "no", "expert", False, "Mutual-exclusion rule from inversion symmetry; IR odd, Raman even."),
    ("enzyme-competitive", "In ideal Michaelis-Menten kinetics with a reversible competitive inhibitor, which parameter remains unchanged: apparent Km or Vmax?", "Vmax", "expert", False, "Competitive inhibition increases apparent Km and leaves asymptotic Vmax unchanged."),
    ("ocean-coriolis", "In the ideal Northern Hemisphere Ekman model, depth-integrated transport is 90 degrees to which side of the surface wind direction?", "right", "expert", False, "NOAA Ekman transport: right in Northern Hemisphere, left in Southern."),
    ("logic-validity", "An argument has false premises but its conclusion necessarily follows from them. Is it valid, sound, both, or neither?", "valid", "expert", False, "Validity concerns entailment; soundness additionally requires true premises."),
    ("pro-law-dates", "A hypothetical statute says a filing is timely within 10 calendar days after service, excluding service day; if the final day is Sunday, extend to Monday. Service occurs Thursday April 4. No holidays apply. Give the deadline as 'April N'.", "April 15", "medium", True, "Closed-world procedural rule: day10 Sunday April14, extended Monday15."),
    ("pro-museum-catalog", "A museum rule selects the earliest secure date, discards dates marked uncertain, and breaks equal secure dates by inventory ID alphabetically. Records: C=1450 secure, A=1450 secure, B=1420 uncertain. Which ID is selected?", "A", "medium", True, "Closed-world rule excludes B; A wins tie with C."),
    ("pro-rna-splice", "A coding DNA strand is 5'-ATGAAAGTCCAGTTT-3'. A specified intron is bases 7 through 12 inclusive, using 1-based numbering. Remove it, then transcribe the remaining coding strand to RNA. Give only the RNA letters.", "AUGAAAUUU", "medium", True, "Bases7..12 GTCCAG removed; coding ATGAAATTT maps T to U."),
    ("pro-sources-conflict", "A supplied source policy ranks signed errata above original editions above summaries, irrespective of date. Original says 24 units; later summary says 30; signed erratum says 26. What value must be reported?", "26", "medium", True, "Closed-world precedence favors signed erratum, not newest summary."),
    ("pro-historiography", "What term names a document erased and reused for new writing while traces of the earlier text remain, rather than a manuscript merely copied from an older exemplar?", "palimpsest", "hard", True, "British Library manuscript terminology: palimpsest, erased/reused writing support."),
    ("pro-philology", "In textual criticism, which three-word Latin maxim says that, other things being equal, the more difficult reading is preferable because copyists tend to simplify?", "lectio difficilior potior", "hard", True, "Standard textual-critical maxim lectio difficilior potior; difficulty is evidence, not an unconditional rule."),
    ("pro-linguistics", "In a language, intransitive subjects pattern with transitive objects, while transitive subjects receive a distinct case. Name the alignment using the two standard case labels separated by a hyphen.", "ergative-absolutive", "hard", True, "S=O absolutive; A ergative, standard alignment definition."),
    ("pro-palaeography", "In textual criticism, an accidental omission caused by a copyist's eye moving between two identical word endings is called what?", "homoeoteleuton", "hard", True, "Text-critical term for same-ending eye-skip omission."),
    ("pro-counterpoint", "In invertible counterpoint at the octave, a third inverts into which interval? Give the ordinal word.", "sixth", "hard", True, "Diatonic interval inversion numbers sum to nine: 3+6=9."),
    ("pro-baroque", "What Renaissance/Baroque musical term denotes a recurring bass pattern underlying changing upper parts? Give the two-word Italian term.", "basso ostinato", "hard", True, "Ground bass; basso ostinato literally persistent bass."),
    ("pro-geophysics", "Which seismic body-wave type cannot propagate through an ideal fluid with zero shear modulus? Use the single capital letter convention.", "S", "hard", True, "Shear-wave velocity sqrt(mu/rho) vanishes when mu=0."),
    ("pro-ocean-density", "Two seawater parcels at equal pressure have equal density but different temperatures and salinities. Their mixture can be denser than either parent because the equation of state is nonlinear. Name this oceanographic process.", "cabbeling", "hard", True, "TEOS-10 Manual: cabbeling is densification by mixing waters of different T/S at initially equal density; https://www.teos-10.org/pubs/TEOS-10_Manual.pdf"),
    ("pro-mineral-optics", "An anisotropic mineral is viewed between crossed polarizers while its stage rotates through 360 degrees. Ignoring special orientations, how many extinction positions occur?", "4", "hard", True, "Extinction each90 degrees when vibration axes align polarizers."),
    ("pro-atmosphere", "In geostrophic balance in the Northern Hemisphere, viewed facing downwind, is lower pressure on the left or right?", "left", "hard", True, "Coriolis to right balances pressure-gradient force toward low on left."),
    ("pro-genetic-code", "In the standard genetic code, give the three RNA stop codons in alphabetical order, comma-separated without spaces.", "UAA,UAG,UGA", "hard", True, "NCBI standard genetic code table1; https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi"),
    ("pro-epigenetic", "In female mammals, dosage compensation usually silences one X chromosome. What visible condensed nuclear structure is associated with that inactive X?", "Barr body", "hard", True, "Inactive X forms Barr body; NHGRI X-inactivation terminology."),
    ("pro-evolution-tree", "A phylogenetic tree is ((A,B),(C,D)). Character states are A=0, B=1, C=1, D=0. Under unordered binary Fitch parsimony, what is the minimum number of state changes on this tree?", "2", "hard", True, "Fitch algorithm: each cherry has disjoint singleton sets so adds1; root sets both {0,1} intersect, adds0."),
    ("pro-economics-index", "A price index weights current versus base prices with base-period quantities. Is it a Laspeyres or Paasche price index?", "Laspeyres", "hard", True, "Laspeyres sum(p_t q_0)/sum(p_0 q_0); Paasche uses q_t."),
    ("pro-economics-excludability", "A resource is rival in consumption but users cannot feasibly be excluded. Classify it as public good, club good, private good, or common-pool resource.", "common-pool resource", "hard", True, "Rivalry plus non-excludability defines common-pool resource."),
    ("pro-logic-modal", "In Kripke semantics, modal axiom T, box p implies p, corresponds to which property of the accessibility relation?", "reflexivity", "hard", True, "Every world accessible to itself iff T valid on the frame."),
    ("pro-photography", "Keeping shutter time and ISO fixed, moving from f/2.8 to f/5.6 changes exposure by how many stops? Give a signed integer, positive for more exposure.", "-2", "hard", True, "Doubling f-number quarters light: two stops less."),
    ("pro-textile", "A textile has five warp ends per repeat. Its single binding point advances by two ends on each successive pick, never binding adjacent ends on successive picks. Name the weave family, choosing plain, twill, or satin.", "satin", "hard", True, "Five-end satin uses step2 or3 distributing isolated binding points; plain alternates and twill advances adjacently."),
    ("pro-archaeology", "In archaeological stratigraphy, an unfilled cut truncates layers A and B, and is later filled by C. Is the cut older or younger than B?", "younger", "hard", True, "Cross-cutting relationships: cut postdates any unit it truncates."),
    ("pro-meteorology", "An unsaturated air parcel rises adiabatically without condensation. Its potential temperature, referenced to the same pressure throughout, does what: increases, decreases, or stays constant?", "stays constant", "hard", True, "Dry adiabatic motion conserves potential temperature."),
    ("pro-neurophysiology", "In a simple passive membrane model, resistance doubles while capacitance halves. The time constant is tau=R*C and the electrotonic length constant is proportional to sqrt(R) with axial resistance fixed. Which increases: time constant only, length constant only, both, or neither?", "length constant only", "hard", True, "tau factor2*0.5=1; length constant factor sqrt2>1."),
    ("pro-astronomy-orbit", "At identical semimajor axis around the same central mass, orbit A has eccentricity 0.2 and orbit B has eccentricity 0.8. In the Newtonian two-body approximation, give the period ratio T_B/T_A.", "1", "hard", True, "Kepler third law depends on semimajor axis, not eccentricity; both periods equal."),
    ("pro-citation-locator", "A supplied citation rule uses section if available, otherwise paragraph, otherwise page. Record has page12, paragraph8, section4.2. Return its locator exactly as 'section N', 'paragraph N', or 'page N'.", "section 4.2", "hard", True, "Closed-world priority section > paragraph > page."),
    ("pro-semantic-scope", "A controlled vocabulary defines 'eligible' as peer-reviewed AND (open-access OR archived). Withdrawn works are ineligible regardless. Records: A=reviewed,open,withdrawn; B=reviewed,archived,not-withdrawn; C=unreviewed,open,archived,not-withdrawn. Which record is eligible?", "B", "hard", True, "Apply withdrawal exception before conjunction/disjunction: A vetoed; C lacks review; B qualifies."),
    ("pro-thermo-maxwell", "For Helmholtz free energy F(T,V) with dF=-S dT-P dV, which derivative equals (partial S/partial V) at fixed T? Choose A=(partial P/partial T) at fixed V, B=its negative. Reply A or B.", "A", "expert", True, "Equality of mixed derivatives: -S_V=-P_T."),
    ("pro-selection-rules", "For electric-dipole transitions in a hydrogenic atom, is a 2s to 1s single-photon transition allowed or forbidden under the orbital angular momentum selection rule?", "forbidden", "expert", True, "Electric-dipole requires delta l=+/-1; s to s has delta l=0."),
    ("pro-point-groups", "A molecule has point group D3h. Does it have an inversion center? Answer yes or no.", "no", "expert", True, "D3h character-table symmetry elements lack inversion; horizontal mirror not sufficient."),
    ("pro-nmr", "In first-order proton NMR, a proton couples equally to three equivalent spin-1/2 neighbors and to no others. Give relative multiplet intensities as comma-separated integers without spaces.", "1,3,3,1", "expert", True, "Binomial expansion for three equivalent spin-half neighbors gives quartet."),
    ("pro-ligand-field", "In an octahedral ligand field, which d-orbital set is lower in energy: t2g or eg?", "t2g", "expert", True, "Octahedral t2g orbitals point between ligand axes and lie below eg."),
    ("pro-chem-isomer", "Consider 2,3-dichlorobutane with identical terminal methyl groups. Of configurations (2R,3R), (2S,3S), and (2R,3S), which is the meso stereoisomer? Return only the parenthesized configuration.", "(2R,3S)", "expert", True, "The R,S form has internal symmetry and is achiral; R,R and S,S are enantiomers."),
    ("pro-population-genetics", "At Hardy-Weinberg equilibrium, a recessive phenotype has frequency 0.09. Assuming complete recessivity, give the heterozygote frequency as a decimal.", "0.42", "expert", True, "q=sqrt(.09)=.3; p=.7; 2pq=.42."),
    ("pro-linkage", "A testcross yields parental classes 420 and 380 and recombinant classes 100 and 100. Give recombination frequency as a decimal, without applying a mapping-function correction.", "0.2", "expert", True, "Recombinants200/total1000=.2; observed fraction not corrected map distance."),
    ("pro-enzyme-uncompetitive", "An inhibitor binds only the enzyme-substrate complex in ideal Michaelis-Menten kinetics. Do apparent Km and Vmax both increase, both decrease, or change in opposite directions?", "both decrease", "expert", True, "Uncompetitive inhibition reduces both by the same alpha-prime factor."),
    ("pro-renal-filtration", "A freely filtered substance is neither secreted nor reabsorbed nor metabolized by kidneys. Its renal clearance measures which rate? Give the full standard name.", "glomerular filtration rate", "expert", True, "Renal clearance of ideal filtration marker equals GFR; physiological definition, not patient advice."),
    ("pro-phonology-features", "A sound change makes a nasal consonant take the place of articulation of a following stop. Is the assimilation progressive or regressive?", "regressive", "expert", True, "Following segment influences preceding segment: regressive/anticipatory assimilation."),
    ("pro-verse-form", "In quantitative classical prosody, a dactylic hexameter's first four feet may be dactyls or spondees; the fifth is a dactyl and sixth has two syllables. Under these assumptions, what is the maximum syllable count?", "17", "expert", True, "Four dactyls provide12 syllables, fifth3, last2: total17."),
    ("pro-music-mode", "In tonal harmony, a German augmented-sixth chord in C minor contains A-flat, C, E-flat, and which altered scale-degree pitch? Give its note name as letter plus # or b.", "F#", "expert", True, "German augmented sixth uses b6,1,b3,#4 in C: Ab C Eb F#."),
    ("pro-earth-age", "An isochron uses x=parent/stable isotope and y=radiogenic daughter/stable isotope; its slope equals exp(lambda*t)-1. If slope is 3, how many parent-isotope half-lives have elapsed?", "2", "expert", True, "exp(lambda*t)=4, lambda*t=ln4; half-life=ln2/lambda, so t=2 half-lives."),
    ("pro-isostasy", "In the Airy model of isostasy, mountains are primarily compensated by variations in crustal thickness or crustal density?", "crustal thickness", "expert", True, "Airy constant-density crust has variable-depth roots; Pratt varies density."),
    ("pro-magnetic-remanence", "An igneous rock cools through magnetic blocking temperatures and retains a magnetic field record. Name the magnetization type, using the full two-word term ending 'magnetization'.", "thermoremanent magnetization", "expert", True, "Thermoremanent magnetization (TRM) is acquired on cooling through blocking temperatures."),
    ("pro-stats-collider", "In a causal DAG A -> C <- B with independent root variables A and B and no other edges, conditioning on C generally opens or closes the path between A and B?", "opens", "expert", True, "Collider conditioning opens an otherwise blocked path under d-separation."),
    ("pro-econ-sterilization", "A central bank buys foreign currency, increasing domestic reserves, then sells domestic bonds to offset that monetary-base increase. What is this offsetting operation called?", "sterilization", "expert", True, "Sterilized foreign-exchange intervention offsets domestic monetary-base effect."),
    ("pro-law-interpretation", "The interpretive canon treats general words following a list of specific items as limited to things of the same kind. Give the Latin two-word name.", "ejusdem generis", "expert", True, "Standard statutory-interpretation canon ejusdem generis; domain knowledge, not legal advice."),
    ("pro-archival-order", "An archive keeps files in the sequence established by their creator, rather than rearranging by modern subject headings. Name this principle using its standard two-word English label.", "original order", "expert", True, "SAA Dictionary: original order concerns internal arrangement, distinct from provenance."),
]

_GENERAL_ALIASES = {
    "grammar-mood": ("irrealis",),
    "geology-dike": ("dyke",),
    "pro-palaeography": ("homeoteleuton", "homoioteleuton"),
    "pro-magnetic-remanence": ("thermoremanent magnetisation",),
    "pro-econ-sterilization": ("sterilisation",),
    "ecology-succession": ("primary",),
    "statistics-design": ("schools", "the school"),
    "archive-provenance": ("principle of provenance", "respect des fonds"),
    "chem-oxidation": ("7",),
    "equilibrium-pressure": ("NH3",),
}


def _text_task(row, category):
    slug, prompt, answer, difficulty, pro, reference = row
    return Task(prompt + " Return only the answer, with no explanation or alternatives.", answer,
                category, pro=pro, id=f"{'pro' if pro else 'axe'}-{category}-{slug}",
                difficulty=difficulty, reference=reference,
                aliases=_GENERAL_ALIASES.get(slug, ()) if category == "general" else ())


GENERAL = tuple(_text_task(row, "general") for row in _GENERAL_ROWS)
REASONING = tuple(_text_task(row, "reasoning") for row in REASON_ROWS)
SOLUTIONS = {name: source for name, prompt, difficulty, pro, source, cases in CODE_ROWS}
CODING = tuple(
    Task(prompt + " Return only self-contained Python 3 standard-library code implementing the requested function.",
         repr([expected for args, expected in cases]), "coding", pro=pro, kind="code",
         test_call="[" + ", ".join(f"{name}(*{args!r})" for args, expected in cases) + "]",
         id=f"{'pro' if pro else 'axe'}-coding-{name}", difficulty=difficulty,
         reference=f"Executable reference SOLUTIONS[{name!r}]; independent boundary-case expected values.",
         test_cases=tuple(cases), solution_name=name)
    for name, prompt, difficulty, pro, source, cases in CODE_ROWS
)
TASKS = GENERAL + CODING + REASONING
TASK_HASH = hashlib.sha256(json.dumps(
    {"revision": TASK_REVISION, "tasks": [asdict(t) for t in TASKS], "solutions": SOLUTIONS},
    ensure_ascii=False, sort_keys=True, separators=(",", ":")
).encode("utf-8")).hexdigest()


def select(*, category: str | None = None, pro: bool = False, difficulty: str | None = None) -> list[Task]:
    """Select one disjoint track, optionally filtering category and difficulty."""
    return [task for task in TASKS if task.pro == pro
            and (category is None or task.category == category)
            and (difficulty is None or task.difficulty == difficulty)]


def select_tasks(*, category: str | None = None, pro: bool = False, difficulty: str | None = None) -> list[Task]:
    """Public descriptive selector; same selection contract as select."""
    return select(category=category, pro=pro, difficulty=difficulty)
