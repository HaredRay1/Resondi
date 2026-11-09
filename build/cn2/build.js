const {
  Document, Packer, Paragraph, TextRun, AlignmentType, ImageRun, PageOrientation, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
} = require('docx');
const FIGS = require('path').join(__dirname, '..', '..', 'figures') + require('path').sep;
const fs = require('fs');

const F = 'Book Antiqua';
const SZ = 24, TSZ = 18;
const CONTENT = 9360;

const T = (t, o = {}) => new TextRun({ text: t, font: F, size: SZ, ...o });
const Tt = (t, o = {}) => new TextRun({ text: t, font: F, size: TSZ, ...o });

const P = (t, o = {}) => new Paragraph({
  spacing: { after: o.after ?? 180, line: 276 },
  alignment: o.align ?? AlignmentType.JUSTIFIED,
  indent: { left: o.left ?? 0, ...(o.hanging ? { hanging: o.hanging } : {}) },
  children: Array.isArray(t) ? t : [T(t)],
});

const H = (t) => new Paragraph({
  spacing: { before: 320, after: 180 },
  children: [T(t, { bold: true, size: 26 })],
});

const SH = (t) => new Paragraph({
  spacing: { before: 220, after: 140 },
  children: [T(t, { bold: true })],
});

const B = (lead, rest) => new Paragraph({
  spacing: { after: 140, line: 276 },
  alignment: AlignmentType.JUSTIFIED,
  indent: { left: 360, hanging: 360 },
  children: [T('● '), T(lead, { bold: true }), T(rest)],
});

const NUM = (n, lead, rest) => new Paragraph({
  spacing: { after: 140, line: 276 },
  alignment: AlignmentType.JUSTIFIED,
  indent: { left: 460, hanging: 460 },
  children: [T(n + '. '), T(lead, { bold: true }), T(rest)],
});

const OBJ = (lead, rest) => [
  new Paragraph({
    spacing: { before: 140, after: 40, line: 276 },
    alignment: AlignmentType.JUSTIFIED,
    children: [T(lead, { bold: true })],
  }),
  new Paragraph({
    spacing: { after: 120, line: 276 },
    alignment: AlignmentType.JUSTIFIED,
    indent: { left: 360 },
    children: [T(rest)],
  }),
];

const cell = (txt, w, { bold = false, shade } = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  shading: shade ? { type: ShadingType.CLEAR, fill: shade, color: 'auto' } : undefined,
  margins: { top: 60, bottom: 60, left: 90, right: 90 },
  children: [new Paragraph({ spacing: { after: 0, line: 230 }, children: [Tt(String(txt), { bold })] })],
});

const TBL = (data, widths, boldLast) => new Table({
  columnWidths: widths,
  width: { size: CONTENT, type: WidthType.DXA },
  rows: data.map((row, r) => new TableRow({
    tableHeader: r === 0,
    children: row.map((t, c) => cell(t, widths[c], {
      bold: r === 0 || (boldLast && r === data.length - 1),
      shade: r === 0 ? 'D9D9D9' : undefined,
    })),
  })),
});

const TBLW = (data, widths, total) => new Table({
  columnWidths: widths,
  width: { size: total, type: WidthType.DXA },
  rows: data.map((row, r) => new TableRow({
    tableHeader: r === 0,
    children: row.map((t, c) => cell(t, widths[c], {
      bold: r === 0,
      shade: r === 0 ? 'D9D9D9' : undefined,
    })),
  })),
});

const TCAP = (n, title, brk) => ([
  new Paragraph({ spacing: { before: 240, after: 20 }, keepNext: true,
    ...(brk ? { pageBreakBefore: true } : {}),
    children: [T('Table ' + n, { bold: true })] }),
  new Paragraph({ spacing: { after: 110 }, keepNext: true,
    children: [T(title, { italics: true })] }),
]);

const FIG = (n, title, file, w, h) => ([
  new Paragraph({ spacing: { before: 240, after: 20 }, keepNext: true,
    children: [T('Figure ' + n, { bold: true })] }),
  new Paragraph({ spacing: { after: 110 }, keepNext: true,
    children: [T(title, { italics: true })] }),
  new Paragraph({
    spacing: { after: 220 },
    alignment: AlignmentType.CENTER,
    children: [new ImageRun({ type: 'png', data: fs.readFileSync(file), transformation: { width: w, height: h } })],
  }),
]);


const GRP = (t) => new Paragraph({
  spacing: { before: 180, after: 90 },
  indent: { left: 360, hanging: 360 },
  children: [T('● '), T(t, { bold: true })],
});

const SUBB = (t) => new Paragraph({
  spacing: { after: 70, line: 266 },
  alignment: AlignmentType.JUSTIFIED,
  indent: { left: 1080, hanging: 360 },
  children: [T('○  ' + t)],
});

const c = [];
const add = (...x) => c.push(...x);

// ───────────────────────────────────────────── COVER
add(new Paragraph({ spacing: { after: 60 }, alignment: AlignmentType.CENTER,
  children: [T('PHILIPPINE STARTUP CHALLENGE XI', { bold: true, size: 26 })] }));
add(new Paragraph({ spacing: { after: 60 }, alignment: AlignmentType.CENTER,
  children: [T('WHEEZARDS', { bold: true, size: 24 })] }));
add(new Paragraph({ spacing: { after: 60 }, alignment: AlignmentType.CENTER,
  children: [T('RESONDI', { bold: true, size: 32 })] }));
add(new Paragraph({ spacing: { after: 320 }, alignment: AlignmentType.CENTER,
  children: [T('CONCEPT NOTE', { bold: true, size: 24 })] }));

// ───────────────────────────────────────────── SUMMARY
add(H('SUMMARY'));
add(P('Resondi is an AI-assisted smart-stethoscope and mobile cardiopulmonary monitoring '
  + 'platform designed to address the difficulty of consistently recording, organizing, and '
  + 'monitoring respiratory and cardiac sounds over time. It is designed as an '
  + 'Internet-of-Things system: a sensing device at the edge, which is built and working, and a '
  + 'mobile gateway and cloud platform, which this funding builds, to store recordings, run the '
  + 'classifier, and route results for professional review. It provides a smart stethoscope with '
  + 'separate lung and heart recording controls, automatic MicroSD organization, guided '
  + 'auscultation, AI-assisted sound analysis, longitudinal monitoring, mode-specific '
  + 'rehabilitation support, and a practitioner review workflow through which every AI-assisted '
  + 'result is confirmed, modified, or returned for a repeat recording. Its key value proposition '
  + 'is to provide patients and healthcare professionals with an organized and accessible system '
  + 'for monitoring cardiopulmonary sound changes and supporting rehabilitation while maintaining '
  + 'professional oversight.'));

// ───────────────────────────────────────────── BACKGROUND
add(H('BACKGROUND OF THE PROBLEM'));
add(P('Respiratory and cardiovascular conditions require repeated assessment and monitoring, '
  + 'particularly for patients undergoing recovery and rehabilitation. In the Philippines, these '
  + 'conditions account for the largest share of registered mortality. Of 701,884 deaths '
  + 'registered in 2024, ischaemic heart diseases led all causes with 134,074, or 19.1 percent '
  + 'of the national total, while pneumonia ranked fourth with 47,260, or 6.7 percent '
  + '(Philippine Statistics Authority [PSA], 2026). These counts are drawn from returns received '
  + 'as of 30 September 2025 and are not adjusted for under-registration, so the true burden is '
  + 'higher than the registered figure. Cardiovascular conditions such as aortic stenosis and '
  + 'mitral regurgitation may '
  + 'produce heart-sound abnormalities that can be assessed through auscultation. However, '
  + 'conventional auscultation relies heavily on proper stethoscope placement, consistent '
  + 'recording techniques, suitable listening conditions, and human interpretation (Bohadana et '
  + 'al., 2014). Recorded findings are also often documented as written observations, making it '
  + 'difficult to preserve and compare the original sounds across different monitoring sessions.'));
add(P('This creates a challenge for longitudinal monitoring and rehabilitation because changes in '
  + 'respiratory or cardiac sound patterns may not be easily tracked over time. The gap is '
  + 'particularly acute in rehabilitation, where pulmonary rehabilitation was available to only '
  + '2.7 percent of people with chronic obstructive pulmonary disease worldwide in 2015 (Lahham & '
  + 'Holland, 2021). Digital stethoscopes can preserve cardiopulmonary sounds as audio recordings '
  + '(Leng et al., 2015), while convolutional neural networks can assist in classifying these '
  + 'recordings into clinically relevant sound categories (Rocha et al., 2019; Tariq et al., '
  + '2022). However, performance in practice remains constrained by background noise and contact '
  + 'artifacts (Shkarupylo et al., 2024), and there is a need for a system that combines '
  + 'standardized sound collection, recording-quality assessment, organized data storage, '
  + 'longitudinal monitoring, and rehabilitation support in one accessible platform. Resondi '
  + 'addresses this need through separate Lung and Heart modes, guided auscultation, automatic '
  + 'organization of recorded sounds, AI-assisted sound analysis, monitoring features, and '
  + 'practitioner-supervised rehabilitation support.'));

// ───────────────────────────────────────────── SOLUTION
add(H('PROPOSED STARTUP SOLUTION'));
add(P('Resondi is an AI-assisted smart-stethoscope and mobile cardiopulmonary monitoring '
  + 'platform that addresses the difficulty of consistently recording, organizing, and monitoring '
  + 'respiratory and cardiac sounds over time. The product is not a better listening instrument. '
  + 'It is a system that converts each act of listening into a structured record that can be '
  + 'retrieved, compared against the same anatomical site weeks later, and reviewed by a licensed '
  + 'practitioner who was not present at the examination.'));

add(SH('The device'));
add(P('The current build is enclosure version 2.0. It pairs an acoustic chest piece, coupled '
  + 'through a printed mount, with an INMP441 digital MEMS microphone on an I²S interface, an '
  + 'ESP32 dual-core microcontroller clocked to 240 MHz, a 16 GB MicroSD card, a 20×4 character '
  + 'LCD on an I²C adapter, two recording buttons for Heart and Lungs modes, two status '
  + 'indicator LEDs, and a 10,000 mAh rechargeable battery. The enclosure is printed in PLA by '
  + 'fused deposition modelling and measures 173 × 80 × 70 mm assembled. The microphone is '
  + 'digital, so no analogue preamplifier stage is required. The design deliberately uses '
  + 'widely available components so that the unit cost remains within reach of facilities that '
  + 'cannot justify an imported electronic stethoscope, which lists at roughly ₱22,000 before '
  + 'shipping and duties (3M, 2025).'));
add(P('Recordings are written to the MicroSD card as 16-bit mono uncompressed PCM WAV at a '
  + '16 kHz sampling rate, approximately 480 kB for a fifteen-second capture, and are filed '
  + 'automatically into separate Heart and Lungs groups with sequential names. The device '
  + 'raises its own 2.4 GHz Wi-Fi access point, so a phone, tablet or computer can connect '
  + 'directly to it and open the Resondi web application the ESP32 itself serves, to start a '
  + 'recording, list what is stored, and play a file back. No internet connection is involved '
  + 'in any of that: the device and the browser talk to each other and to nothing else.'));
add(P('Table 1 gives the full specification of the current build.'));
add(...TCAP(1, 'Technical Specification, Enclosure Version 2.0'));
add(TBL([
  ['Item', 'Specification'],
  ['Main controller', 'ESP32 development board, 32-bit dual-core Xtensa LX6, up to 240 MHz'],
  ['Audio sensor', 'INMP441 digital omnidirectional MEMS microphone, I²S interface'],
  ['Microphone output', '24-bit digital; firmware records at 16-bit'],
  ['Recording format', 'WAV, uncompressed PCM, 16 kHz, 16-bit, mono, 256 kbps'],
  ['Recording duration', '15 seconds per capture in the current firmware'],
  ['File size', 'Approximately 480 kB per recording'],
  ['Storage', '16 GB MicroSD card; separate Heart and Lungs groups, sequential filenames'],
  ['Display', '20 × 4 character LCD, I²C interface'],
  ['Controls', 'Heart and Lungs recording buttons, two status LEDs, power rocker switch'],
  ['Wireless', '2.4 GHz Wi-Fi, IEEE 802.11 b/g/n, device-hosted access point'],
  ['Local interface', 'Resondi web application served by the ESP32 at http://192.168.4.1'],
  ['Power', '10,000 mAh rechargeable battery'],
  ['Enclosure', 'PLA, fused deposition modelling, 173 × 80 × 70 mm assembled'],
], [2400, 6960]));
add(P('Figure 1 locates these components on the enclosure itself.'));
add(...FIG(1, 'Resondi Enclosure Version 2.0, Front Face and Exploded Assembly',
  FIGS + 'Resondi-Device-Components.png', 580, 188));
add(P('Figure 2 sets out how these components relate, from the acoustic chest piece through '
  + 'the microcontroller to storage and the wireless interface. The case is printed rather '
  + 'than moulded at this stage, which is why the unit cost carries a printed PLA housing '
  + 'and why that cost falls once silicone vacuum casting replaces it at volume. The printed '
  + 'case is a prototype enclosure, not a field one: PLA softens at around 60 °C, a '
  + 'temperature the inside of a vehicle reaches in tropical sun, so a heat-resistant '
  + 'enclosure is part of the hardware refinement this funding covers.'));
add(...FIG(2, 'Hardware Block Diagram of the Resondi Smart Stethoscope',
  FIGS + 'figB_device.png', 580, 217));

add(SH('The system as an Internet-of-Things architecture'));
add(P('Resondi is designed as a three-tier Internet-of-Things system, and the tiers are worth '
  + 'separating because each carries a different cost, a different failure mode, and a '
  + 'different state of completion. At the edge, the ESP32 samples the microphone over I²S, '
  + 'writes a completed recording to MicroSD with its metadata — anatomical site, mode, '
  + 'timestamp, duration — and serves its own Wi-Fi access point so that a browser on the same '
  + 'network can control it. That tier exists and works today.'));
add(P('The two tiers above it are what this funding round builds, and the document is explicit '
  + 'about that rather than describing them in the present tense. The mobile application is '
  + 'the gateway: it will pull completed recordings from the device, carry them to the '
  + 'platform, and is the only component that requires an internet connection; ₱38,000 is '
  + 'allocated to it. The platform is the cloud tier: it will store recordings against a '
  + 'patient record, run the classifier, and present results to the reviewing practitioner; '
  + '₱48,000 of cloud infrastructure and operation funds it. The device as it stands today '
  + 'records, organises and serves its own recordings locally, and no cloud access, remote '
  + 'internet access or external network integration is part of the current configuration.'));

add(P('Two properties separate this from a conventional connected-sensor deployment, and both '
  + 'follow from where the device has to work. Capture is session-based rather than '
  + 'continuous: the device is not a monitor streaming telemetry but an instrument that records '
  + 'a defined examination at defined sites, which is why a recording is addressed by '
  + 'anatomical location and not by timestamp alone. And the architecture is store-and-forward '
  + 'by design. A barangay health station with no connectivity can complete a full examination '
  + 'offline; the recordings persist on MicroSD and will synchronise once the gateway reaches a '
  + 'network. Connectivity is a convenience in this system rather than a precondition, which is '
  + 'the opposite of the assumption most connected medical devices make and the reason this one '
  + 'suits the setting.'));

add(P('Two capabilities follow from the architecture rather than from any new hardware. Model '
  + 'updates reach the installed base through the platform, so a unit already in the field '
  + 'improves as the classifier is retrained, without being returned or replaced; this is a '
  + 'substantial part of what the subscription funds. Device health reporting — battery '
  + 'condition, firmware version, storage state, and date of last calibration — travels the '
  + 'same channel and would let a cluster of facilities be supported without a site visit. It '
  + 'is a planned extension, not a present capability, and is not claimed as one.'));

add(SH('The workflow'));
add(P('A recording moves through the platform in six stages:'));
add(NUM(1, 'Mode selection. ', 'The user selects Lung Mode or Heart Mode, which determines the '
  + 'auscultation sequence, the storage path, and the analysis applied.'));
add(NUM(2, 'Guided placement. ', 'The application directs the user to standardized anatomical '
  + 'locations — six lung fields and a tracheal reference, or the cardiac valve points — using an on-screen '
  + 'map and written guidance.'));
add(NUM(3, 'Capture and automatic organization. ', 'The device records and files each capture '
  + 'into its corresponding lung or heart folder, tagged with anatomical site, mode, duration, '
  + 'and timestamp. This metadata is what makes later comparison possible; an untagged recording '
  + 'cannot be matched to its predecessor.'));
add(NUM(4, 'AI-assisted analysis. ', 'Recordings are converted into time–frequency '
  + 'representations and classified by a convolutional neural network over one-second '
  + 'windows, returning one of four categories together with a confidence score. The deployed '
  + 'model takes mel-frequency cepstral coefficients as its input representation and was '
  + 'trained against the ICBHI 2017 Respiratory Sound Database (Rocha et al., 2019). It is '
  + 'compiled to an eight-bit quantised build for on-device inference. A feature-fusion architecture, in which '
  + 'mel-spectrogram, MFCC and chromagram representations are processed by parallel branches '
  + 'and combined before classification (Tariq et al., 2022), is the planned successor and is '
  + 'not what the reported results describe.'));
add(NUM(5, 'Practitioner review. ', 'Every AI-assisted result is presented to a licensed '
  + 'practitioner alongside the original recording. The practitioner may confirm, disagree with, '
  + 'modify, or request a repeat. No AI output is released to a patient without that step, and no '
  + 'AI output overwrites a professional judgment.'));
add(NUM(6, 'Longitudinal comparison and rehabilitation. ', 'Confirmed results are stored against '
  + 'the patient record so that a recording taken today can be compared with the same anatomical '
  + 'site from a previous session. Where a practitioner approves it, the platform releases '
  + 'mode-specific rehabilitation activities: guided breathing exercises in Lung Mode, and, once a '
  + 'practitioner has recorded a diagnosis and cleared the patient, cardiac activity guidance in '
  + 'Heart Mode.'));
add(P('Figure 3 presents the six stages as a single flow. Two of the transitions are loops rather '
  + 'than steps forward: a practitioner who judges a recording unusable returns the user to '
  + 'capture, and a patient under follow-up re-enters at guided placement so that the new '
  + 'recording is taken at the same anatomical site as the last.'));
add(...FIG(3, 'Six-Stage Recording and Review Workflow',
  FIGS + 'figA_workflow.png', 580, 162));
add(P('Figure 4 shows the same stages as the application renders them. The screens are '
  + 'captures from the working build rather than mock-ups, which is why the practitioner '
  + 'queue in the fifth panel is populated with test recordings. Stage six is not shown: '
  + 'longitudinal comparison requires two sessions at the same anatomical site, and the '
  + 'build does not yet hold a pair to display.'));
add(...FIG(4, 'The Workflow as Rendered in the Application',
  FIGS + 'fig_app_workflow.png', 580, 229));
add(SH('Auscultation sites and recording protocol'));
add(P('Guided placement is only useful if the sites are fixed, named, taken in a known order, '
  + 'and the same ones the models were trained against. Resondi\u2019s site definitions are '
  + 'therefore drawn from the recording schemes of the two reference datasets rather than invented '
  + 'for the device. Lung Mode follows the regional scheme described for digital-stethoscope '
  + 'recording by Huang et al. (2023), in which the chest surface is sampled over the upper, '
  + 'middle, and lower lobes on both sides; every site maps onto one of the chest-location codes '
  + 'carried in the ICBHI 2017 database \u2014 trachea, anterior left and right, posterior left '
  + 'and right, and lateral left and right (Rocha et al., 2019). Heart Mode uses the four valve '
  + 'points at which the CirCor DigiScope recordings were collected (Oliveira et al., 2022), '
  + 'together with Erb’s point, which is captured for the practitioner but not classified. In '
  + 'both modes the numbering is the order of capture, not merely a label: the application will '
  + 'not advance to the next site until the current one has been recorded, which is what keeps a '
  + 'session comparable with the one before it.'));

add(P('Figure 5 gives the protocol in full: the seven lung-mode sites — six lung fields and the '
  + 'tracheal reference taken before them — the '
  + 'five cardiac points, and the order in which each is taken. In Lung Mode the sequence works '
  + 'downward in left\u2013right pairs \u2014 the anterior upper fields, then the lateral fields '
  + 'with the arm raised, then the posterior fields with the patient seated and the arms brought '
  + 'forward to draw the scapulae aside. In Heart Mode it runs from the base of the heart to its '
  + 'apex. The cardiac panel also marks where the valves themselves lie, because the listening '
  + 'points sit downstream of the valves in the direction of blood flow rather than directly over '
  + 'them; that is why the aortic point falls to the right of the sternum although the valve is '
  + 'central. Table 2 gives the surface landmark and dataset code for every lung-mode site, '
  + 'and Table 3 does the same for Heart Mode. Each of the seven lung-mode captures maps '
  + 'onto exactly one ICBHI chest-location code, so no two recordings are filed under the '
  + 'same label.'));
add(...FIG(5, 'Auscultation Sites, Listening Sequence and Recording Protocol',
  FIGS + 'fig_ausc_combined.png', 600, 832));

add(...TCAP(2, 'Lung Mode Auscultation Sites and Their Surface Landmarks', true));
add(TBL([
  ['Site', 'Surface landmark', 'Region sampled', 'ICBHI code'],
  ['Tc', 'Suprasternal notch, over the trachea', 'Central airway (reference capture)', 'Tc'],
  ['1', 'Second intercostal space, right midclavicular line', 'Right upper lobe', 'Ar'],
  ['2', 'Second intercostal space, left midclavicular line', 'Left upper lobe', 'Al'],
  ['3', 'Fourth to fifth intercostal space, right mid-axillary line', 'Right middle lobe', 'Lr'],
  ['4', 'Fourth to fifth intercostal space, left mid-axillary line', 'Lingula', 'Ll'],
  ['5', 'Infrascapular, T8\u2013T10, right of the spine', 'Right lower lobe', 'Pr'],
  ['6', 'Infrascapular, T8\u2013T10, left of the spine', 'Left lower lobe', 'Pl'],
], [760, 3680, 3280, 1640]));
add(new Paragraph({ spacing: { before: 120, after: 180 },
  children: [T('Note. ', { italics: true, size: 20 }),
             T('Regional scheme after Huang et al. (2023); location codes after Rocha et al. (2019). '
               + 'ICS = intercostal space. The tracheal capture is a reference recording and is '
               + 'not classified as a lung field, so the seven sites yield six classified lung '
               + 'fields. The seven captures correspond one-to-one with the seven ICBHI chest '
               + 'locations, so no code is reused.', { size: 20 })] }));

add(...TCAP(3, 'Heart Mode Auscultation Sites and Their Surface Landmarks'));
add(TBL([
  ['Site', 'Surface landmark', 'Valve assessed', 'CirCor code'],
  ['A', 'Second intercostal space, right sternal border', 'Aortic', 'AV'],
  ['P', 'Second intercostal space, left sternal border', 'Pulmonary', 'PV'],
  ['E', 'Third intercostal space, left sternal border', 'Erb\u2019s point \u2014 captured, not classified', '\u2014'],
  ['T', 'Fourth to fifth intercostal space, left lower sternal border', 'Tricuspid', 'TV'],
  ['M', 'Fifth intercostal space, left midclavicular line (apex)', 'Mitral', 'MV'],
], [760, 3900, 3060, 1640]));
add(new Paragraph({ spacing: { before: 120, after: 180 },
  children: [T('Note. ', { italics: true, size: 20 }),
             T('Landmarks after Oliveira et al. (2022). The CirCor DigiScope dataset contains '
               + 'labelled recordings for the four valve points only, so Erb\u2019s point is recorded '
               + 'and filed for the reviewing practitioner but is not passed to the classifier.',
               { size: 20 })] }));

add(P('Each capture then follows the same sequence, which the application displays as on-screen '
  + 'instructions:'));
add(NUM(1, 'Prepare the room and the patient. ', 'The setting is made as quiet as it can be, and '
  + 'the diaphragm is placed in direct contact with skin. Recording through clothing both '
  + 'attenuates the signal and adds friction artifact (Bohadana et al., 2014).'));
add(NUM(2, 'Position the patient. ', 'Seated upright with the arms brought forward for the '
  + 'posterior and lateral lung sites, and seated or supine for the anterior sites. In Heart Mode '
  + 'the patient is supine for sites A, P, E, and T, then rolled into the left lateral decubitus '
  + 'position for site M, which brings the cardiac apex against the chest wall.'));
add(NUM(3, 'Set the breathing pattern. ', 'In Lung Mode the patient breathes through an open '
  + 'mouth, somewhat deeper than at rest, so that airflow is sufficient to generate audible breath '
  + 'sounds. In Heart Mode the patient breathes quietly and normally, so that breath sounds do not '
  + 'mask the cardiac cycle.'));
add(NUM(4, 'Record for a fixed interval. ', 'The protocol calls for twenty seconds per site in '
  + 'Lung Mode, which captures at least three complete respiratory cycles at a normal adult '
  + 'rate, and fifteen seconds per site in Heart Mode, which captures at least fifteen cardiac '
  + 'cycles at a resting rate. Published digital-auscultation protocols use intervals of fifteen '
  + 'to thirty seconds for the same reason (Huang et al., 2023). The firmware on the current '
  + 'build records a fixed fifteen-second capture in both modes, so a lung site is taken as two '
  + 'consecutive recordings until the interval is made selectable; that change is a firmware '
  + 'revision and carries no additional component cost.'));
add(NUM(5, 'Work in left\u2013right pairs. ', 'Sites are visited as bilateral pairs at each level '
  + 'before the sequence moves downward, so that any asymmetry between the two sides appears in '
  + 'adjacent records rather than being separated by several minutes of examination.'));
add(NUM(6, 'Repeat where the recording is unusable. ', 'The platform scores each capture for '
  + 'audio clarity and returns a quality grade of good, acceptable or poor before analysis. A '
  + 'poor capture is repeated rather than classified, and the workflow returns to this stage '
  + 'rather than advancing. The check currently takes about 145 seconds, which is the '
  + 'constraint on using it routinely in a consultation.'));
add(NUM(7, 'Tag and file. ', 'Each capture is written with its site code, mode, duration, and '
  + 'timestamp, which is what allows a recording to be compared with its predecessor. A recording '
  + 'taken at an unspecified point on the chest cannot be.'));

add(P('Fixing the protocol is not administrative tidiness. Unaided auscultation is a weak test '
  + 'taken on its own: a meta-analysis of thirty-four studies in adults with acute pulmonary '
  + 'pathology found a pooled sensitivity of 37 percent against a specificity of 89 percent, and '
  + 'attributed much of that weakness to variation in how clinicians listen and in how they '
  + 'describe what they hear (Arts et al., 2020). The same analysis concluded that auscultation '
  + 'retains its place where imaging is not available, which describes most of the facilities this '
  + 'platform is built for. Two things recover information that a single unstructured examination '
  + 'loses. The first is sampling more than one site: in a study of 2,402 multi-channel lung '
  + 'recordings, classification accuracy rose from roughly 0.79 on a single auscultation position '
  + 'to roughly 0.92 across four (Kim et al., 2025). The second is comparability over time, which '
  + 'requires that the same site be recorded the same way at every visit. Resondi is built around '
  + 'both.'));
add(P('Figure 6 sets out the planned feature-fusion architecture for stage four, in which three '
  + 'time–frequency representations of the same recording are classified in parallel and combined '
  + 'before a single prediction is produced (Tariq et al., 2022).'));
add(...FIG(6, 'Planned Convolutional Neural Network Feature-Fusion Architecture',
  FIGS + 'figD_cnn.png', 580, 226));

add(SH('Human oversight as architecture, not policy'));
add(P('The practitioner review stage is a structural feature rather than a disclaimer. Current '
  + 'evidence does not support autonomous interpretation: a systematic review of pediatric '
  + 'lung-sound AI models reported approximately 91 percent pooled sensitivity but limited '
  + 'external validation (Park et al., 2025). Keeping a clinician in the loop is therefore both '
  + 'the clinically responsible design and the one that keeps the platform within decision support '
  + 'rather than diagnosis, with the lighter regulatory burden that follows.'));

add(SH('Evidence from initial testing'));
add(P([T('The prototype has been built and measured, and the results are reported here as they '
  + 'were found (Malimban, 2026). On signal acquisition the device performs well: mean signal '
  + 'strength was approximately 45 dB against approximately 32 dB for a conventional acoustic '
  + 'stethoscope under the same conditions. Because the decibel scale is logarithmic, that '
  + '13 dB difference corresponds to roughly four and a half times the sound-pressure '
  + 'amplitude, and it is reported that way rather than as a ratio of the decibel figures '
  + 'themselves. Recordings were graded by qualified healthcare professionals against '
  + 'predetermined criteria, with 68 percent rated good, 25 percent acceptable, and 7 percent '
  + 'poor. Recordings were obtained '
  + 'in three settings at ambient noise levels of 24 dB in a quiet room, 35 dB in a hospital '
  + 'ward, and 42 dB in a community area, indicating that capture remains possible across '
  + 'the range of conditions a rural health unit presents. The margin is not uniform: against '
  + 'a 45 dB signal the quiet room leaves roughly 21 dB of headroom, the ward about 10 dB, and '
  + 'the community area only about 3 dB. That narrowing margin, rather than any failure to '
  + 'capture, is what makes noise reduction the first development priority. End-user acceptance '
  + 'was assessed with 27 respondents across Puerto Princesa City using an instrument adapted '
  + 'from the Unified Theory of Acceptance and Use of Technology, together with three patients '
  + 'at a private hospital under the supervision of an attending physician who reviewed and '
  + 'consented to the procedure. Across twelve five-point Likert items overall acceptance was '
  + '3.95, interpreted as Agree on the study\u2019s acceptance scale. Performance expectancy '
  + 'and effort expectancy each returned a weighted mean of 4.09, regulatory assurance 3.84, '
  + 'and social influence 3.63. Twenty-one of twenty-seven respondents reported that peers '
  + 'encourage use of the device and twenty of twenty-seven that their institution would '
  + 'provide the resources to run it; access to training and technical support drew the least '
  + 'certain response, with eight answering yes, twelve unsure and seven no.')]));
add(P('Classification agreement is the weak result and is stated plainly. Of fifteen paired '
  + 'recordings compared against reference labels, six produced matching classifications, an '
  + 'agreement rate of 40 percent with a 95 percent confidence interval of 19.8 to 64.3 percent. '
  + 'That interval contains both chance agreement and a usefully performing classifier, and the '
  + 'present sample cannot distinguish between them. The study protocol specified Cohen’s '
  + 'kappa alongside percentage agreement, but kappa on fifteen paired observations is not a '
  + 'stable statistic, so raw agreement is the headline here; the funded evaluation reports '
  + 'kappa, per-class recall and the full confusion matrix on a sample large enough to carry '
  + 'them. Against the 25 percent agreement expected by chance '
  + 'across four classes, an exact binomial test returns p = 0.148: the result is not '
  + 'distinguishable from guessing, and 8 of 15 agreements would have been needed to reach '
  + 'conventional significance. No test of marginal homogeneity is reported, because such a '
  + 'test asks about the direction of errors rather than about agreement, and would be without '
  + 'power at this sample size. The reference labels were assigned by the consulting '
  + 'pulmonologists, whose honoraria sit in the clinical validation line; whether that '
  + 'assessment was blinded to the model output is not recorded in the study documentation, '
  + 'and the funded prospective evaluation specifies independent assessment, blinded to the '
  + 'model output, so that the next agreement figure does not carry the same ambiguity. '
  + 'Fifteen recordings is far too small a sample to support any '
  + 'conclusion about accuracy, and none is drawn here. The study’s own conclusion is that '
  + 'it does not yet provide sufficient empirical evidence to establish definitive conclusions '
  + 'regarding classification accuracy, recording quality, response time, reliability, or user '
  + 'acceptance, and that further validation in actual healthcare settings is required. That '
  + 'finding is the reason clinical validation carries ₱120,000 of the requested funding, the largest single category, and a '
  + 'patient-wise baseline evaluation is the second phase of the implementation plan.'));

add(P('Held-out performance on the development corpus is stronger than field agreement, and the '
  + 'gap is itself a finding. The corpus holds 19,246 labelled five-second samples, split into '
  + '15,392 for training and 3,854 held out for testing, and the network classifies them in '
  + 'one-second windows. On the held-out test partition the unquantised model returns 71.1 '
  + 'percent accuracy, an area under the ROC curve of 0.96, and weighted precision, recall and '
  + 'F1 of 0.84, 0.83 and 0.83. On the validation partition the same model returns 83.4 '
  + 'percent and the eight-bit quantised build 83.7 percent; the quantised build, which is the '
  + 'one deployed, has not yet been scored against the held-out test partition, and that run '
  + 'is part of the Phase 2 evaluation. Per class, F1 is highest for '
  + 'the wheeze-dominant category at 0.95 and lowest for the normal category at 0.63, where the '
  + 'model most often returns an uncertain result rather than a confident one. Against this, '
  + 'agreement with pulmonologist labels on device recordings was 40 percent. Three things '
  + 'separate the two figures, and the first of them is now established rather than suspected. '
  + 'The corpus partitions were drawn at random over individual samples, with no metadata key '
  + 'grouping them by parent recording or subject. Since the five-second samples were cut at '
  + 'roughly a one-second stride, segments sharing four of their five seconds of audio sit on '
  + 'both sides of the split, so neither corpus figure is independent of the training data and '
  + 'both are optimistic. The labels compound it: each window carried its patient’s diagnosis '
  + 'rather than the sound actually present in that second, and a pneumonia patient does not '
  + 'crackle in every second, so the one signal consistent across a patient’s windows is that '
  + 'patient’s own acoustic signature. A model can score well on such a split by recognising who '
  + 'is breathing rather than what the breath contains. Beyond that, the corpus is European and the recordings Filipino, and '
  + 'the corpus was captured on research equipment while the recordings were made on this '
  + 'device. A subject-wise re-partition and retraining is the first task funded in Phase 2. '
  + 'No corpus figure is offered here as evidence of field performance, and the 40 percent '
  + 'remains the only estimate drawn from data the model had not seen in any form.'));

add(P('The population gap is addressed in two steps rather than one, and the first costs '
  + 'nothing. HF_Lung_V1 (Hsu et al., 2021) provides 9,765 recordings from approximately 279 '
  + 'subjects collected in Taiwan, released open-access under a Creative Commons Attribution '
  + 'licence \u2014 roughly ten times the recording count of ICBHI 2017, and from an East Asian '
  + 'population rather than a European one. Its event-level labels for continuous and '
  + 'discontinuous adventitious sounds map onto the four categories used here, so it can be '
  + 'folded into training without changing the output scheme, and it is already the third run '
  + 'of the evaluation plan. Locally collected, clinically labelled Philippine recordings are '
  + 'the second step and the only component obtainable from no public source, which is what '
  + 'the \u20b146,000 recording and annotation line funds. Asian representation is therefore '
  + 'not absent from the plan; Filipino representation is what remains to be bought.'));

add(P('One structural point is stated plainly because it bears on how the output should be read. '
  + 'The network was trained against the diagnostic categories carried in the source corpus, and '
  + 'the platform presents its four outputs to the practitioner as the sound patterns those '
  + 'categories characteristically produce: the asthma category is displayed as high-pitched '
  + 'wheezing, bronchiolitis as wheezing with crackles, pneumonia as crackles, and the healthy '
  + 'category as a normal or soft field. The practitioner therefore sees an acoustic '
  + 'description rather than a disease name, which is the behaviour the regulatory position in '
  + 'this document depends on. The mapping between the model\u2019s output and the displayed label '
  + 'is a design decision rather than something the network learned, and validating that mapping '
  + 'against pulmonologist-assigned sound-pattern labels is part of the Phase 2 evaluation.'));

add(SH('Current state and development priority'));
add(P('The working prototype records lung and heart sounds separately and organizes them '
  + 'automatically, and respiratory-sound classification is implemented. Cardiac sound '
  + 'classification is in development; the device currently captures and organizes heart '
  + 'recordings for practitioner review. Automated recording-quality assessment is implemented '
  + 'and runs before classification: the platform scores each capture for audio clarity and '
  + 'returns a grade of good, acceptable or poor, so a poor capture is repeated rather than '
  + 'analysed. The limitation is speed, not absence. The quality check takes approximately '
  + '145 seconds against about 4 seconds for classification itself, which is too long to sit '
  + 'comfortably inside a consultation and is the single clearest target for optimisation. '
  + 'Active noise reduction is not yet implemented. Noise and contact artifacts are a '
  + 'recognized constraint across digital auscultation generally rather than a defect unique '
  + 'to this prototype (Shkarupylo et al., 2024), and the margin above ambient narrows to '
  + 'roughly 3 dB in a community area. Bringing the quality check down to a usable latency and '
  + 'adding noise reduction is the first development priority under the requested funding, '
  + 'supported by ₱102,000 of AI development and ₱42,000 of hardware refinement including '
  + 'higher-sensitivity microphones.'));

add(SH('Alignment with the Sustainable Development Goals'));
add(P('The priority is SDG 3 – Good Health and Well-Being, and three of its targets are '
  + 'addressed directly. Target 3.4 seeks to cut premature mortality from non-communicable '
  + 'disease by one third; Resondi supports earlier and comparable cardiopulmonary assessment '
  + 'at the primary level, where ischaemic heart disease and pneumonia together account for '
  + 'roughly one in four Filipino deaths. Target 3.8 seeks universal access to quality '
  + 'essential health services; the practitioner review workflow gives a rural health unit '
  + 'without a resident physician a route to clinical review of a recording rather than of a '
  + 'written note. Target 3.c seeks to increase and retain the health workforce in developing '
  + 'countries; guided acquisition at standardized sites is what allows a midwife or nurse to '
  + 'perform a repeatable examination, which is task shifting supported by method rather than '
  + 'by exhortation. Nationally, the Universal Health Care Act (Republic Act No. 11223, 2019) '
  + 'moves financing and delivery toward the primary level this device is built for '
  + '(United Nations, 2015).'));
add(P('Two further goals are supported rather than led. SDG 9 – Industry, Innovation and '
  + 'Infrastructure is supported by an affordable IoT and AI health device designed and built '
  + 'in the Philippines and engineered to operate without a network connection. SDG 4 – '
  + 'Quality Education is supported by the institutional licence channel, through which '
  + 'nursing and medical schools use recorded, labelled auscultation for hands-on teaching. '
  + 'Stating one priority goal rather than three is deliberate: a priority that includes '
  + 'everything is not a priority.'));

// ───────────────────────────────────────────── OBJECTIVES
add(H('OBJECTIVES'));
add(...OBJ('To develop a smart stethoscope capable of separately recording and organizing lung '
  + 'and heart sounds.', 'This allows the device to identify the type of sound being recorded and '
  + 'automatically organize the files into their corresponding lung or heart folders.'));
add(...OBJ('To provide guided auscultation through standardized anatomical lung and cardiac '
  + 'locations.', 'The application will guide users on where to place the stethoscope and how to '
  + 'follow a consistent recording process.'));
add(...OBJ('To assess the quality of recorded cardiopulmonary sounds before analysis.',
  'The system will evaluate factors such as background noise, signal strength, recording '
  + 'duration, clipping, and motion artifacts to help ensure usable recordings. This capability is '
  + 'not present in the current prototype and is the first development priority under the '
  + 'requested funding.'));
add(...OBJ('To implement AI-assisted analysis of respiratory and cardiac sound patterns.',
  'The system will analyze suitable recordings to identify relevant sound patterns for monitoring '
  + 'and rehabilitation purposes.'));
add(...OBJ('To establish longitudinal monitoring of respiratory and cardiac sound changes across '
  + 'monitoring and rehabilitation sessions.', 'Previous recordings will be stored and compared '
  + 'with later recordings to help track changes in sound patterns over time.'));
add(...OBJ('To provide Lung and Heart modes with rehabilitation-support features tailored to the '
  + 'selected cardiopulmonary condition.', 'Lung Mode will focus on respiratory monitoring and '
  + 'breathing exercises, while Heart Mode will provide cardiac monitoring and '
  + 'practitioner-approved rehabilitation activities appropriate to the selected heart condition.'));
add(...OBJ('To provide healthcare professionals with organized recordings, monitoring '
  + 'information, and AI-assisted results for professional review.', 'Practitioners will be able '
  + 'to review patient records and monitoring results to support supervised care and '
  + 'rehabilitation.'));
add(...OBJ('To maintain structured patient records that support continuous monitoring and '
  + 'rehabilitation.', 'The platform will organize sound recordings, monitoring information, and '
  + 'rehabilitation progress so they can be reviewed across multiple sessions.'));
add(P('These objectives aim to develop Resondi as an integrated cardiopulmonary monitoring and '
  + 'rehabilitation platform. What exists today is stated precisely, because the distinction '
  + 'matters to what the funding buys. The working prototype performs guided sound '
  + 'acquisition, automated sound organization, automated recording-quality assessment, and '
  + 'AI-assisted analysis of lung recordings. Quality assessment is implemented and runs '
  + 'before classification; its limitation is speed rather than absence, at approximately '
  + '145 seconds. Longitudinal comparison views, the practitioner review dashboard, and '
  + 'mode-specific rehabilitation support exist as designed workflows rather than as '
  + 'finished software, and ₱38,000 of the requested funding is allocated to building '
  + 'them. Cardiac sound classification is likewise in development; the device captures and '
  + 'organizes heart recordings for practitioner review but does not yet classify them. '
  + 'Through separate Lung and '
  + 'Heart modes, Resondi is designed to help users and healthcare professionals consistently '
  + 'monitor respiratory and cardiac sound patterns and track progress across rehabilitation '
  + 'sessions.'));

// ───────────────────────────────────────────── TARGET MARKET
add(H('TARGET MARKET / BENEFICIARIES'));
add(P('Resondi is sold to institutions and used by the health workers inside them. Who buys '
  + 'and who benefits are separated here because they are not the same, and the business '
  + 'model depends on the distinction: every sale is business-to-business, and patients are '
  + 'reached through a deploying institution under practitioner supervision rather than as '
  + 'direct purchasers. The buying segments are listed in the order the commercial plan '
  + 'approaches them.'));
add(SH('Buying segments, in order of approach'));

add(GRP('Rural Health Units and Municipal Health Centres'));
[
  'Give midwives and nurses a second set of ears where no physician is resident.',
  'Capture at standardized sites so a recording can be compared with the one before it.',
  'Hold recordings on the device when connectivity fails, and synchronise later.',
  'Route captures to a municipal health officer or a remote practitioner for review.',
  'Reduce unnecessary referral trips by attaching a reviewable recording to the decision.',
].forEach((t) => add(SUBB(t)));

add(GRP('Nursing and Medical Schools'));
[
  'Teach auscultation from real, labelled recordings rather than from live encounters alone.',
  'Give students repeated practice at standardized sites with guided placement.',
  'Let instructors review and assess a student’s recording technique from the stored capture.',
  'Carry a lighter regulatory burden than clinical deployment, which is why this channel opens first.',
].forEach((t) => add(SUBB(t)));

add(GRP('Private Clinics and Secondary Hospitals'));
[
  'Support cardiopulmonary monitoring and rehabilitation services already being delivered.',
  'Maintain structured patient records and longitudinal monitoring information.',
  'Support follow-up monitoring where it is professionally supervised.',
  'Improve the organization and accessibility of cardiopulmonary assessment data.',
].forEach((t) => add(SUBB(t)));

add(SH('Users and beneficiaries'));

add(GRP('Healthcare Workers (primary users)'));
[
  'Review recorded lung and heart sounds through the mobile application.',
  'Access AI-assisted sound analysis alongside the original recording to support professional review.',
  'Monitor changes in respiratory and cardiac sound patterns across sessions.',
  'Review patient rehabilitation information and progress.',
  'Guide patients during auscultation and rehabilitation activities.',
  'Use stored recordings and monitoring information to support follow-up assessment.',
].forEach((t) => add(SUBB(t)));

add(GRP('Patients (indirect beneficiaries, not purchasers)'));
[
  'Are recorded by a health worker at standardized sites, rather than recording themselves.',
  'Have their cardiopulmonary sound patterns tracked across visits instead of assessed once.',
  'Participate in respiratory or cardiac rehabilitation activities released by a practitioner.',
  'Keep an organized record that a healthcare professional can review at a later visit.',
  'Are reached through a deploying institution; Resondi is not sold to patients and is not '
  + 'intended for unsupervised use at home.',
].forEach((t) => add(SUBB(t)));

add(GRP('Schools as teaching environments'));
[
  'Use Resondi as an educational and training tool for students in nursing, medicine, and other health-related programs.',
  'Provide students with hands-on practice in proper lung and heart sound auscultation techniques.',
  'Support guided learning through standardized auscultation procedures and recording instructions.',
  'Allow students to record and review lung and heart sounds as part of supervised clinical skills training.',
  'Provide AI-assisted sound analysis as a learning aid to help students recognize and differentiate common cardiopulmonary sound patterns.',
  'Help instructors demonstrate proper auscultation techniques and assess students’ recording procedures and performance.',
  'Support the development of students’ clinical assessment and sound-identification skills before and during clinical exposure.',
  'Provide organized recordings that can be used for classroom demonstrations, skills laboratory activities, and supervised case discussions.',
  'Support repeated practice and learning without requiring students to rely solely on live patient encounters.',
  'Serve as a supplementary educational platform for cardiopulmonary assessment and rehabilitation concepts.',
].forEach((t) => add(SUBB(t)));

add(P('Overall, Resondi connects deploying institutions, the health workers inside them, and '
  + 'the patients they serve through a single platform for guided auscultation, '
  + 'cardiopulmonary monitoring, rehabilitation support, and organized longitudinal '
  + 'records. The commercial relationship is with the institution throughout.'));

// ───────────────────────────────────────────── VALUE PROPOSITION
add(H('VALUE PROPOSITION'));
add(P('Resondi’s value proposition is not that it listens to the chest. A stethoscope already '
  + 'does that, and does it well. The value is that Resondi turns each act of listening into a '
  + 'structured, organized, reviewable record that can be compared against the same patient and '
  + 'the same chest location weeks later, and that a licensed practitioner confirms or corrects.'));
add(P('Conventional auscultation produces a written observation. The sound itself is gone the '
  + 'moment the examination ends, which means a follow-up assessment cannot be compared against '
  + 'the original, a second opinion cannot be sought without re-examining the patient, and a '
  + 'midwife in a remote barangay cannot have a finding reviewed by a physician who is not '
  + 'physically present. Existing electronic stethoscopes preserve the audio but stop there: they '
  + 'do not guide placement, do not separate lung from heart capture, do not organize recordings '
  + 'by anatomical site for longitudinal comparison, and do not carry a workflow for practitioner '
  + 'review. Resondi is built around the gap between a recording and a usable record.'));
add(SH('Four differentiators define the offering:'));
add(B('Guided acquisition at standardized sites. ', 'The application directs the user to '
  + 'standardized lung and cardiac auscultation points, separates lung from heart capture, and '
  + 'tags every recording with its anatomical location, mode, and timestamp. Standardizing where '
  + 'and how a recording is taken is the precondition for everything downstream: without it, a '
  + 'difference between two sessions could be a change in the patient or merely a change in where '
  + 'the chest piece was placed.'));
add(B('Longitudinal comparison at the level of the individual site. ', 'Because every recording '
  + 'is tagged with its anatomical location and timestamp, a recording taken today can be compared '
  + 'against the same site from a previous session. This converts auscultation from a series of '
  + 'disconnected snapshots into a trajectory, which is what recovery and rehabilitation '
  + 'monitoring actually require.'));
add(B('Human-in-the-loop by design. ', 'Every AI-assisted result is presented for practitioner '
  + 'review, and the practitioner can confirm, disagree with, modify, or request a repeat. The AI '
  + 'never overwrites a professional judgment. This reflects the limits of current evidence: a '
  + 'systematic review of pediatric lung-sound AI models reported approximately 91 percent pooled '
  + 'sensitivity but limited external validation (Park et al., 2025). It is both the clinically '
  + 'responsible design and the commercially durable one, because it keeps the platform in the '
  + 'role of decision support rather than diagnosis.'));
add(B('Unified lung and heart workflow on affordable hardware. ', 'Separate Lung and Heart modes, '
  + 'with rehabilitation support released under practitioner supervision, run on an ESP32-based '
  + 'device built from widely available components. This places the platform within reach of '
  + 'facilities that cannot justify the cost of imported electronic stethoscopes and have no '
  + 'cardiopulmonary documentation system at all. Respiratory exercises are drawn from published '
  + 'pulmonary rehabilitation guidance (Lahham & Holland, 2021) and released once a practitioner '
  + 'approves them; cardiac activity guidance is withheld until a practitioner has recorded a '
  + 'diagnosis and cleared the patient, since a detected murmur is not itself a diagnosis.'));
add(SH('What Resondi does not yet do'));
add(P('Automated recording-quality assessment is implemented and runs before classification, '
  + 'but it takes approximately 145 seconds, against about 4 seconds for the classification '
  + 'itself. A practitioner can use it deliberately; they cannot use it on every capture in a '
  + 'busy clinic. Reducing that latency is the first development priority funded by this '
  + 'request. Active noise reduction is not yet implemented at all, and the signal margin '
  + 'above ambient narrows to roughly 3 dB in a community area, which is where it matters '
  + 'most. Noise and contact artifacts are a recognized constraint across the digital '
  + 'auscultation field rather than a defect unique to this prototype (Shkarupylo et al., '
  + '2024). Until the latency comes down, practical quality control still rests with the '
  + 'practitioner, who reviews every AI-assisted result alongside the recording itself and can '
  + 'request a repeat. Together these absorb ₱102,000 of AI development and ₱42,000 of '
  + 'hardware refinement, including higher-sensitivity microphones.'));
add(P('Figure 7 sets out Resondi’s position against the three alternatives a facility '
  + 'realistically has today, including the capability still in development.'));
add(...FIG(7, 'Resondi Value Proposition Against Existing Alternatives',
  FIGS + 'fig1_value_proposition.png', 560, 360));
add(P('The underlying advantage is one that a better-funded competitor cannot acquire by copying '
  + 'the hardware or the model, both of which are reproducible. It is the consented, locally '
  + 'labelled body of cardiopulmonary recordings captured on Resondi hardware under actual '
  + 'Philippine clinical conditions, which accumulates with every deployment and improves the '
  + 'platform for every subsequent user.'));

// ───────────────────────────────────────────── BUSINESS MODEL
add(H('BUSINESS MODEL'));
add(P('Resondi operates a hardware-enabled software model, sold business-to-business. The smart '
  + 'stethoscope is the entry point, but the recurring value and the recurring revenue sit in the '
  + 'platform that organizes, analyzes, and preserves the recordings the device produces, and '
  + 'routes them for review. Figure 8 presents the model as a canvas.'));

add({ __section: 'landscape' });
add(...FIG(8, 'Business Model Canvas for Resondi',
  FIGS + 'Figure-08-Business-Model-Canvas.png', 940, 634));
add({ __section: 'portrait' });

add(P('A canvas is read in three parts. The right-hand blocks describe the market — who the '
  + 'customer is, how they are reached, and what relationship is maintained with them. The '
  + 'left-hand blocks describe the infrastructure required to serve that market. The two lower '
  + 'blocks describe the economics that result. A model is coherent when the right side justifies '
  + 'the left and the bottom balances.'));
add(P('On the market side, the segments block separates three roles that are often conflated: the '
  + 'buyer is an institution holding a budget, the user is a midwife, nurse, or rural health '
  + 'physician, and the beneficiary is a patient in a community a physician visits infrequently. '
  + 'Every revenue-bearing segment is therefore business-to-business, and the segments are ordered '
  + 'by adoption sequence rather than by size of need. The channels block pairs each segment with '
  + 'a route, with institutional sale and local government procurement carrying early revenue and '
  + 'distributors extending reach only once there is a registered product to distribute.'));
add(P('On the infrastructure side, the key resources block names the asset that actually matters. '
  + 'The hardware is reproducible from published component lists and the model architecture is '
  + 'published in the literature, so neither is defensible alone. What a competitor cannot acquire '
  + 'by copying is the consented, locally labelled body of cardiopulmonary recordings captured on '
  + 'Resondi hardware under Philippine clinical conditions, which grows with every deployment. '
  + 'The activities block is deliberately balanced between building the product and selling it, '
  + 'and it leads with the honest technical priority: a faster recording-quality check and '
  + 'noise reduction, the capability gap between a prototype that captures sound and a product '
  + 'that can be trusted in a noisy rural health unit.'));
add(P('The lower blocks tie directly to the financial requirement. The ₱500,000 seed divides into '
  + 'ten categories, of which production working capital funds the first batch of saleable '
  + 'units and cloud infrastructure sets recurring cost. The device sells at ₱8,000 against a fully loaded unit cost of approximately '
  + '₱4,000, so it is profitable from the first production unit rather than dependent on the '
  + 'subscription to cover a hardware loss, and the subscription is a second margin stream on top '
  + 'of it. The canvas also records the live constraint: automated quality screening runs '
  + 'before analysis but takes about 145 seconds, which is what the first tranche of AI '
  + 'development is directed at.'));

add(SH('How value is created'));
add(P('Value is created at the point of acquisition. By guiding placement, separating lung and '
  + 'heart capture, and tagging every recording with its anatomical site and mode, Resondi '
  + 'produces a dataset that is comparable across sessions, which an unguided recording never is. '
  + 'The AI layer and the longitudinal comparison features are only meaningful because the '
  + 'acquisition is standardized first.'));
add(SH('How value is delivered'));
add(P('The smart stethoscope is distributed to a facility together with access to the mobile '
  + 'platform. Health workers record under guidance; the platform stores and organizes the '
  + 'recordings by patient and anatomical site; the practitioner reviews and confirms AI-assisted '
  + 'results through the review workflow; and patients follow mode-specific rehabilitation '
  + 'activities under that supervision. Delivery to public facilities runs through LGU and '
  + 'Department of Health procurement channels and through donor-funded deployments; delivery to '
  + 'private clinics and schools runs through direct sale and medical distributors.'));
add(SH('How value is captured'));
add(P('Revenue is captured through one entry-point stream, one primary recurring stream, and two '
  + 'secondary ones. The device sells '
  + 'at ₱8,000 against a fully loaded unit cost of approximately ₱4,000, giving roughly fifty percent '
  + 'gross margin from the first production unit while remaining about a third the price of an '
  + 'imported electronic stethoscope. The platform subscription is therefore a second margin '
  + 'stream rather than a mechanism for recovering a hardware loss. Table 4 summarizes the four '
  + 'streams.'));
add(...TCAP(4, 'Revenue Streams and Payment Basis'));
add(TBL([
  ['Stream', 'Who pays', 'Basis', 'Role'],
  ['Device sale', 'LGU, hospital, clinic, school', '₱8,000 one-time, per unit', 'Entry point'],
  ['Platform subscription', 'Facility', '₱1,500 to ₱4,500 per facility per month by tier', 'Primary'],
  ['Institutional licence', 'Nursing and medical schools', '₱30,000 per school per year', 'Secondary'],
  ['Donor-funded deployment', 'NGO, development agency', 'Per-deployment grant', 'Secondary'],
], [2000, 2600, 2900, 1860]));
add(SH('Unit economics'));
add(P('Three distinct cost figures appear in this model and are kept separate. The fully loaded '
  + 'cost of one production unit, once the design is frozen, is approximately ₱4,000. The '
  + 'bill of materials for a single VER 2.0 unit totals ₱2,735 (Team Wheezards, 2026) and states that '
  + 'battery protection and a charging circuit are not included in that total; adding those, '
  + 'together with the connectors, strain relief, finished enclosure and spares allowance a '
  + 'saleable unit requires beyond a prototype, brings components to approximately ₱3,400. '
  + 'Assembly, calibration, functional test and packaging account for the remaining ₱600. '
  + 'The design-iteration cost is approximately ₱14,000 per unit, because the ₱42,000 hardware '
  + 'refinement allocation also absorbs single-quantity retail pricing, failed casing prints, '
  + 'board revisions, and test failures that a refinement phase necessarily consumes. The '
  + 'selling price is ₱8,000. The first figure governs unit economics; the second justifies the '
  + 'hardware line in '
  + 'the financial requirement; the third is what a customer pays. Table 5 derives the pricing '
  + 'from these figures.'));
add(...TCAP(5, 'Unit Economics and Pricing Derivation'));
add(TBL([
  ['Component', 'Derivation', 'Amount'],
  ['Device selling price', 'Set at roughly one third the cost of the imported alternative', '₱8,000'],
  ['Fully loaded unit cost', '₱2,735 bill of materials plus ₱665 battery protection, charging and production allowance, giving ≈ ₱3,400 of components; plus ₱600 assembly, calibration and packaging, design frozen', '≈ ₱4,000'],
  ['Device gross margin', 'Selling price less fully loaded unit cost', '₱4,000 (50%)'],
  ['Platform operating cost', 'Metered cloud, storage and backup per active facility at pilot scale, carried at', '₱350 per month'],
  ['Support and replacement reserve', 'Remote support plus device replacement provision', '₱250 per month'],
  ['Monthly contribution', 'Subscription less platform cost and reserve', '₱900 per month'],
  ['Subscription price', 'Sum of the three monthly components', '₱1,500 per facility per month'],
], [2500, 4300, 2560]));
add(SH('Subscription tiers, bundles and onboarding'));
add(P('The ₱1,500 subscription derived above is the entry tier and the only one the financial '
  + 'projections assume. Two tiers above it are priced for facilities that need more than '
  + 'capture, analysis, review and visit-to-visit comparison, and they are available after the '
  + 'funded build rather than today. Every tier carries the same safety-critical functions — the recording-quality check '
  + 'and mandatory practitioner review — because a cheaper plan must not mean a less-reviewed '
  + 'result. Table 6 sets out the ladder.'));
add(...TCAP(6, 'Subscription Tiers and Their Monthly Contribution'));
add(TBL([
  ['', 'Essential', 'Clinical', 'Network'],
  ['Price per facility per month', '₱1,500', '₱2,900', '₱4,500'],
  ['Minimum facilities', '1', '1', '3 (cluster)'],
  ['Devices and users per facility', '1 device, 2 users', '3 devices, 8 users', '5 devices, unlimited users'],
  ['Cloud allowance', '₱350', '₱450', '₱600'],
  ['Service and replacement reserve', '₱250', '₱250', '₱250'],
  ['Review operations', '—', '—', '₱350'],
  ['Monthly contribution', '₱900', '₱2,200', '₱3,300'],
  ['Added capability', 'Guided capture, quality check, AI classification, practitioner review, offline capture, model updates; same-site comparison across visits and cloud backup once the funded build delivers them', 'Rehabilitation module, role-based access and audit log, monthly facility report', 'Cross-facility routing to a remote clinician, cluster dashboard, DOH and LGU data export, quarterly clinical review, annual refresher training'],
  ['Available', 'Now; comparison and cloud backup after the funded build', 'After the funded build', 'After the funded build'],
], [2300, 2270, 2370, 2420]));
add(P('The capabilities that sit above Essential are not chosen arbitrarily. Role-based access '
  + 'and audit logging and the practitioner dashboard behind cross-facility routing are funded '
  + 'lines inside the ₱38,000 mobile-application allocation in Table 15, so the pricing ladder '
  + 'and the funding request describe the same build, which is why neither upper tier is offered '
  + 'before it exists. The longitudinal comparison views, funded from the same allocation, are '
  + 'deliberately placed in Essential rather than above it. Same-site comparison across visits '
  + 'is the capability this document is built around, and the entry tier is the only one the '
  + 'projections assume, so every modelled facility must receive it. Holding it back for a '
  + 'higher price would make the product that is pitched different from the product that is '
  + 'counted.'));
add(P('Bundles exist because a facility buying a device and a subscription in the same '
  + 'procurement is one decision rather than two, and because an LGU budget line is easier to '
  + 'defend as a single annual figure than as a capital purchase plus a recurring charge. One '
  + 'discipline governs all of them: no bundle discount is taken out of the ₱600 per facility '
  + 'per month that pays for cloud operation and the device replacement reserve. On Essential, '
  + 'where contribution is exactly the ₱900 the projections assume, the discount comes out of '
  + 'device margin alone and the subscription is charged in full. On the two higher tiers, where '
  + 'contribution is ₱2,200 and ₱3,300, part of the discount can come from the subscription and '
  + 'the ₱900 floor still holds with room to spare. Table 7 states the four bundles and where '
  + 'each discount is absorbed.'));
add(...TCAP(7, 'Bundles, Prepaid Twelve Months'));
add(TBL([
  ['Bundle', 'Contents', 'If bought separately', 'Bundle price', 'Where the discount is absorbed', 'Contribution retained'],
  ['Starter', '1 device, Essential, 12 months prepaid', '₱26,000', '₱24,500', '₱1,500 off the device; subscription charged in full', '₱900 per month; device margin ₱2,500 (38%)'],
  ['Clinic', '3 devices, Clinical, 12 months prepaid', '₱58,800', '₱52,000', '₱3,000 off the devices, ₱3,800 off the subscription', '₱1,883 per month'],
  ['Cluster', '3 facilities with 1 device each, Network, 12 months prepaid', '₱186,000', '₱168,000', '₱4,500 off the devices, ₱13,500 off the subscription', '₱2,925 per facility per month'],
  ['Teaching', 'Institutional licence, 2 devices, 12 months', '₱46,000', '₱42,000', '₱4,000 off the devices; licence charged in full', 'Licence intact at ₱30,000'],
], [1180, 2080, 1360, 1180, 2160, 1400]));
add(P('Two onboarding offers lower the cost of the first commitment, and neither of them is a '
  + 'concession the cash model has to absorb. A new facility pays nothing for its first month on '
  + 'Essential, which is not an added cost because the model already begins the monthly '
  + 'contribution in the month after acquisition rather than the month of it: the device margin '
  + 'is received on acquisition and the first subscription month was never counted. A new '
  + 'deployment may also run on Clinical for its first sixty days before choosing a tier, which '
  + 'costs the ₱100 monthly difference in cloud allowance for two months, or ₱200 per facility '
  + 'once. Offers do not stack: a facility takes either the free first month on a month-to-month '
  + 'subscription or a prepaid bundle, not both.'));
add(P('The projections in this document model every facility at Essential and at the full '
  + '₱1,500. A tier mix is not assumed, because at ten facilities in commercial Year 1 any '
  + 'assumed mix would be guesswork, and because the ladder can only raise contribution above '
  + '₱900, never below it. The tiers and bundles are stated here as how pricing scales once the '
  + 'product does, and they are a proposal rather than a validated price: no buyer has yet '
  + 'agreed to ₱2,900, and the willingness-to-pay question is one of the items the pre-launch '
  + 'interviews with facility budget-holders are designed to answer.'));
add(P('Revenue years in this document are years of commercial operation, not years from the '
  + 'date of funding. Commercial operation begins in month 15 of the implementation plan, at '
  + 'Phase 6, and the two are kept distinct throughout: the eighteen-month development programme '
  + 'and the revenue model overlap by four months rather than running in parallel from month one. '
  + 'Within Phase 6 the education channel opens first, because an auscultation teaching tool sold '
  + 'to a nursing or medical school carries a lighter regulatory burden than a clinical '
  + 'deployment; sales to rural health units follow registration.'));
add(P('Each facility contributes ₱4,000 in device margin on acquisition and ₱900 per month '
  + 'thereafter, giving ₱14,800 in its first year. Each school licence contributes ₱25,800 after '
  + 'platform cost — ₱30,000 less ₱4,200 of annual platform cost. Commercial Year 1 — ten facilities and three schools — gives a total '
  + 'run-rate contribution of approximately ₱225,400, which returns roughly forty-five percent of the '
  + '₱500,000 seed. Commercial Year 2 follows the Year 2 waypoint within the obtainable market '
  + 'of Figure 9 — twenty-five facilities and seven '
  + 'schools — and is projected at approximately ₱510,600: ₱60,000 of device margin on fifteen '
  + 'new units, ₱270,000 of subscription, and ₱180,600 from school licences. The weighting '
  + 'shifts decisively toward recurring revenue, which is ₱450,600 of that total.'));
add(P('Commercial Year 3 completes the obtainable market of Figure 9 at fifty facilities and '
  + 'fifteen institutions. Twenty-five further facilities are acquired across the year and the '
  + 'twenty-five already installed pay a full twelve months, while seven school licences renew '
  + 'and eight are added. On the same acquisition ramp used throughout, Year 3 contributes '
  + 'approximately ₱885,700 in cash, taking cumulative contribution from first sale to '
  + 'approximately ₱1,488,500 by the end of month 36. The year is included because the '
  + 'investor return resolves within it and because the market section commits to a '
  + 'three-year obtainable market; it is a projection rather than a plan, and no spending '
  + 'commitment in this document depends on it.'));
add(P('The annual figures are run-rate totals: they state what ten facilities and three '
  + 'schools contribute over twelve months once acquired, not what is collected in the calendar '
  + 'year during which they are acquired. The distinction is material. Under the acquisition '
  + 'ramp assumed here — facilities coming online at roughly one a month, subscription billing '
  + 'from the month after installation, and school licences paid annually in advance — cash '
  + 'contribution in commercial Year 1 is ₱175,900 rather than the ₱225,400 run-rate, because a '
  + 'facility installed in month ten pays two months of subscription within that year and not '
  + 'twelve. Commercial Year 2 is likewise ₱426,900 in cash against a ₱510,600 run-rate. The payback calculation uses the cash figures throughout; the run-rate figures '
  + 'state the steady-state value of an acquired customer. The two answer different questions '
  + 'and are not alternative estimates of the same one.'));
add(P('Working capital after the first batch follows from those cash figures and is stated '
  + 'rather than assumed. The ₱40,000 production allocation funds ten units. The fifteen units '
  + 'required in commercial Year 2 cost approximately ₱60,000 in components and assembly, which '
  + 'is funded from Year 1 cash contribution and from deposits against confirmed purchase '
  + 'orders, not from the seed. Because facilities are acquired across the year rather than at '
  + 'its start, units are built in batches as orders are confirmed, so the working-capital '
  + 'requirement at any one time is a fraction of the annual component cost.'));
add(P('Two conservatisms are built into these figures and are stated so that they are not '
  + 'mistaken for omissions. School hardware is excluded: the ₱40,000 of commercial Year 1 device margin is '
  + 'the ten facilities only, and any school that also purchases a unit at ₱8,000 adds ₱4,000 of '
  + 'margin that is not counted here. Second, the ₱350 platform operating cost is set at pilot '
  + 'scale, where the fixed component of hosting is spread across the fewest facilities; it is '
  + 'funded for the first twelve months of commercial service by the cloud operation line in '
  + 'Table 14, and the per-facility figure falls thereafter as the installed base grows, so ₱900 '
  + 'of monthly contribution is a floor rather than a ceiling. Storage cost does rise with the '
  + 'volume of recordings retained, which works in the other direction; the ₱350 is set to '
  + 'absorb that growth across the pilot period and is reviewed at the end of it. Neither '
  + 'adjustment has been taken into the projection.'));
add(SH('Why the model is sustainable'));
add(P('Three properties make the model durable rather than merely viable. First, the subscription '
  + 'is tied to a capability that degrades without it: model updates, secure storage, and the '
  + 'practitioner review workflow are ongoing services, not a one-time feature. Second, switching '
  + 'costs rise with use, because a facility’s longitudinal record lives in the platform and has '
  + 'no value outside it. Third, every deployment contributes consented, labelled recordings that '
  + 'improve classification performance for all users, so the product strengthens as the installed '
  + 'base grows rather than becoming commoditized.'));
add(P('The education channel deserves particular note. Sold to nursing and medical schools as an '
  + 'auscultation teaching tool, Resondi carries a substantially lighter regulatory burden than a '
  + 'clinical decision-support deployment, generates revenue during the period when clinical '
  + 'validation is still under way, and places the device in the hands of practitioners who will '
  + 'later specify equipment in their own facilities.'));

// ───────────────────────────────────────────── MARKET ANALYSIS
add(H('MARKET ANALYSIS'));
add(SH('Demand'));
add(P('Respiratory and cardiovascular disease together account for the largest share of mortality '
  + 'in the Philippines. The Philippine Statistics Authority recorded 701,884 registered deaths in '
  + '2024; ischaemic heart disease was the leading cause with 134,074 deaths, or 19.1 percent of '
  + 'the total, and pneumonia ranked fourth with 47,260 deaths, or 6.7 percent (PSA, 2026). Both '
  + 'are conditions in which auscultation forms part of routine assessment and in which repeated '
  + 'assessment over time governs clinical decisions.'));
add(P('The care that would use Resondi is delivered overwhelmingly at the primary level, and '
  + 'that level is under-resourced. Primary care accounts for roughly four percent of total health '
  + 'spending while hospital care accounts for about half, and only half of Filipinos can reach a '
  + 'rural health unit within thirty minutes of travel (Department of Health [DOH], 2020). The '
  + 'diagnostic equipment gap at this level is the market.'));
add(P('Early engagement has begun in Palawan. The team has opened discussions with rural health '
  + 'units, private clinics, and nursing and medical schools in and around Puerto Princesa City '
  + 'about pilot deployment and classroom use. These are exploratory conversations rather than '
  + 'commitments, and no purchase order or memorandum of agreement is in place; they are '
  + 'reported here because they establish that the segments named below are reachable from where '
  + 'the team already sits, not because they constitute traction.'));
add(SH('Market size'));
add(P('Figure 9 sets out the addressable, serviceable, and obtainable market.'));
add(...FIG(9, 'Addressable, Serviceable, and Obtainable Market',
  FIGS + 'fig2_market.png', 540, 282));
add(P('Department of Health facility registry figures record approximately 26,504 barangay health '
  + 'stations, 2,682 rural health units, and 836 municipal and city health centres nationwide '
  + '(DOH, 2025), giving a total addressable market of roughly 30,000 public facilities that '
  + 'perform auscultation. The serviceable available market is narrower: approximately 3,500 rural '
  + 'health units and municipal or city health centres that hold a budget line and have a resident '
  + 'clinician able to perform the review function the platform depends on, together with nursing '
  + 'and medical schools. The serviceable obtainable market over the first three years is '
  + 'approximately 50 facilities and 15 institutions, beginning with 10 facilities and 3 schools '
  + 'in commercial Year 1 and rising to roughly 25 and 7 in commercial Year 2, concentrated in '
  + 'MIMAROPA and partner '
  + 'local government units.'));
add(SH('Competitive landscape'));
add(P('Table 8 compares Resondi against the three alternatives a Philippine primary care '
  + 'facility realistically has today, together with the hospital information systems available '
  + 'at tertiary level.'));
add(...TCAP(8, 'Competitive Landscape for Cardiopulmonary Auscultation in Philippine Primary Care'));
add(TBL([
  ['Alternative', 'Indicative cost to the buyer', 'Position', 'Principal limitation'],
  ['Conventional acoustic stethoscope', '₱500 – ₱3,000', 'Universal; present in every facility',
    'Produces no record; nothing to compare or review later'],
  ['Imported electronic stethoscope', '₱22,000+ before shipping and duties', 'Preserves audio; premium segment',
    'No guided placement, no site-level organization, no review workflow; cost beyond an RHU equipment budget'],
  ['Phone voice memo and written notes', 'Free', 'Improvised; already in informal use',
    'Unstructured, no site tagging, no mode separation, no review workflow'],
  ['Hospital information systems', 'Institutional licence', 'Structured records in tertiary facilities',
    'Absent at primary level; store text, not the sound itself'],
  ['Resondi', '₱8,000 device + ₱1,500 per facility per month', 'Primary care and education',
    'Quality assessment runs before analysis but takes about 145 seconds; active noise reduction and cardiac classification are still in development'],
], [1900, 2100, 2200, 3160]));
add(P('The 3M Littmann CORE Digital Stethoscope lists at approximately USD 379, equivalent to '
  + 'roughly ₱22,000 before shipping and import duties (3M, 2025), and comparable devices from Eko '
  + 'Health sit in the same band. That price point explains why electronic auscultation has not '
  + 'reached Philippine primary care: the device costs more than the annual equipment allocation '
  + 'of many rural health units. Resondi enters at ₱8,000 against a fully loaded unit cost of roughly '
  + '₱4,000, which converts a capital purchase decision into an operating one while leaving the '
  + 'device profitable from the first unit rather than dependent on the subscription to cover a '
  + 'hardware loss.'));
add(P('No competitor currently combines guided acquisition at standardized sites, lung and heart '
  + 'mode separation, site-level longitudinal comparison, and a practitioner review workflow at a '
  + 'price point reachable by a Philippine rural health unit. That combination, rather than any '
  + 'single feature, defines the open position.'));
add(SH('Named device comparison'));
add(P('Table 8 compares categories of alternative. Table 9 compares Resondi against the '
  + 'specific devices a judge or a reviewer is most likely to raise, feature by feature. '
  + 'Prices are manufacturer or principal-retailer list prices in United States dollars as '
  + 'published in October 2026 and exclude shipping, duties and local margin; a Philippine '
  + 'buyer pays more than the figure shown.'));

add({ __section: 'landscape' });
add(...TCAP(9, 'Device Feature Comparison Against Named Alternatives'));
add(TBLW([
  ['Device', 'List price', 'AI on lung sounds', 'Guided placement',
   'Same-site comparison across visits', 'Works without a network', 'Available to a Philippine buyer'],
  ['Resondi', '₱8,000 + ₱1,500 per facility per month',
   'Yes — four lung sound patterns; field agreement is a 40 percent baseline and retraining is funded',
   'Yes — seven lung sites in a fixed order', 'Yes — by anatomical site',
   'Yes — store-and-forward on MicroSD', 'Designed and priced for it'],
  ['Eko CORE 500', 'USD 449',
   'No — cardiac only (structural murmur, atrial fibrillation)',
   'Cardiac only, four points, behind the Eko+ subscription', 'Not documented',
   'No — recording and analysis require an internet connection',
   'Hardware importable; Eko+ is not sold in the Philippines, so the AI is unavailable'],
  ['Eko CORE 300 (released 22 October 2026)', 'USD 199–249',
   'No — suspected structural murmur only', 'No', 'Not documented',
   'Acoustic listening only; AI and recording need a connection',
   'United States at launch; Eko+ is not sold in the Philippines'],
  ['3M Littmann CORE (Eko-powered)', 'USD 379',
   'No — murmur only; atrial fibrillation requires a CORE 500',
   'Cardiac only, behind the Eko+ subscription', 'Not documented', 'No',
   'Hardware importable; Eko+ is not sold in the Philippines'],
  ['Thinklabs One', 'USD 499', 'None', 'Position tagging in the companion app only',
   'Not documented', 'Yes — amplified listening, but no storage on the device',
   'Import only'],
  ['HD Medical HD Steth', 'USD 499 bundle (2021 price; current availability unverified)',
   'Claimed in marketing, but the FDA clearance states the device is not intended for diagnosis',
   'No', 'Not documented', 'Not documented', 'Not found'],
  ['StethoMe', 'Not published',
   'Yes — pathological respiratory sounds including wheeze; home and pediatric use',
   'No', 'Not documented', 'Not documented', 'Not found; CE marked for Europe'],
  ['E-Steth (UP College of Medicine and DOST-PCHRD)',
   'Not sold', 'None', 'No', 'No', 'Yes',
   'Philippine development at technology readiness level 5; not yet purchasable'],
  ['Conventional acoustic stethoscope', '₱500 – ₱3,000', 'None', 'No', 'No', 'Yes',
   'Universal'],
], [1700, 1500, 2600, 1900, 1700, 2300, 2700], 14400));
add({ __section: 'portrait' });

add(P('Three findings in Table 9 matter more than the price column. First, no vendor '
  + 'reviewed documents comparison of a new recording against an earlier recording from the '
  + 'same anatomical site on the same patient. Eko comes closest, recording position metadata '
  + 'and patient profiles, but publishes no comparison feature. That absence, rather than any '
  + 'single capability, is the position Resondi occupies. Second, guided placement exists in '
  + 'the market only as a four-point cardiac exam behind a subscription; no reviewed device '
  + 'guides a non-expert through a lung field sequence. Third, every AI capability in the '
  + 'table is cardiac except StethoMe, which is a consumer product for children in Europe.'));

add(P('The Philippine position is the sharpest of the four. Eko’s artificial intelligence '
  + 'is delivered through the Eko+ subscription, and Eko publishes the list of countries in '
  + 'which that subscription is sold: the United States, Canada, twenty European countries, '
  + 'Australia and New Zealand. The Philippines is not among them, and neither is any member '
  + 'of ASEAN. A Philippine facility can therefore import the hardware and receive amplified '
  + 'listening, but cannot license the analysis that justifies the price. Eko also stores all '
  + 'cloud recordings within the United States, which a Philippine deploying institution must '
  + 'weigh against its obligations under the Data Privacy Act. Resondi is not competing '
  + 'against these products in the Philippine market, because in the Philippine market their '
  + 'intelligence is not for sale.'));

add(P('The cost gap is narrower than it was. The Eko CORE 300, released on 22 October 2026 '
  + 'at between USD 199 and USD 249, is the first cleared device with murmur analysis priced '
  + 'near Resondi’s ₱8,000, and it is reported here rather than omitted. It detects one '
  + 'cardiac finding, offers no lung analysis, no guided lung placement and no longitudinal '
  + 'comparison, and its analysis is unavailable in the Philippines. The honest reading is '
  + 'that price alone is no longer a defensible position, and that the combination of guided '
  + 'lung acquisition, site-level longitudinal comparison, a practitioner review workflow and '
  + 'offline capture is.'));

add(P('For local comparison, the Department of Science and Technology’s Philippine Council '
  + 'for Health Research and Development reports that electronic stethoscopes available in the '
  + 'Philippines cost at least ₱30,000 to ₱40,000, in its account of E-Steth, a locally '
  + 'developed acoustic-electronic stethoscope from the University of the Philippines College '
  + 'of Medicine. E-Steth carries no artificial intelligence and remains at technology '
  + 'readiness level 5, which is to say it is a working prototype seeking investment rather '
  + 'than a product. It is the closest Philippine precedent to Resondi and is cited here as '
  + 'evidence that the need is recognised domestically, not as a competitor.'));

add(SH('Demand drivers'));
add(P('Three structural trends support adoption. The Universal Health Care Act (Republic Act No. '
  + '11223, 2019) reorients financing and service delivery toward primary care and integrated '
  + 'province-wide health systems, creating both budget and mandate at the facility level Resondi '
  + 'targets. The shortage of physicians in rural and island provinces makes task shifting '
  + 'unavoidable, and a tool that lets a midwife capture a reviewable recording for later '
  + 'physician assessment supports that shift directly. And remote delivery of rehabilitation has '
  + 'proved feasible in comparable low-resource settings (Hossain et al., 2025), while the '
  + 'normalization of telemedicine since 2020 has left facilities more willing to adopt digital '
  + 'documentation than they were five years ago.'));
add(SH('Barriers'));
add(P('Three barriers are equally real and are addressed in the operations plan rather than '
  + 'discounted here. Medical device registration under the Food and Drug Administration Act '
  + '(Republic Act No. 9711, 2009) must precede any clinical sale, which is why the education '
  + 'channel opens first and why no clinical revenue is modelled before registration. Local '
  + 'government procurement cycles are annual and slow, '
  + 'which is why the subscription is priced as an operating rather than capital commitment. And '
  + 'the prototype’s recording-quality check takes about 145 seconds, too slow for routine use '
  + 'in a consultation, and bringing it down is the first technical milestone funded by this request.'));
add(SH('Operating environment'));
add(P('Table 10 summarizes the operating environment across six external factors.'));
add(...TCAP(10, 'PESTLE Analysis of the Resondi Smart Stethoscope System'));
add(TBL([
  ['Factor', 'Strengths', 'Challenges', 'Opportunities', 'Threats'],
  ['Political',
    'Aligns with the Universal Health Care Act’s primary-care orientation and the Philippine eHealth agenda',
    'Adoption depends on LGU budget approval and DOH facility standards',
    'DOH and DOST-PCHRD health technology programmes offer funding and endorsement pathways',
    'Shifts in health policy or LGU leadership can suspend procurement mid-cycle'],
  ['Economic',
    '₱8,000 entry price against ₱22,000+ for imported electronic stethoscopes; ~50% gross margin per unit',
    'Recurring subscription is a new budget line for most rural health units',
    'Primary care receives only 4% of health spending, a gap UHC implementation is intended to close',
    'Limited LGU budgets; component import costs sensitive to exchange rate'],
  ['Social',
    'Supports task shifting to midwives and nurses where physicians are scarce',
    'Health workers require training; patients unfamiliar with guided self-recording',
    'Growing acceptance of telemedicine and digital records since 2020',
    'Preference for familiar acoustic stethoscopes; scepticism toward AI in clinical settings'],
  ['Technological',
    'Store-and-forward edge device that works with no connectivity at all: records to MicroSD and serves its own Wi-Fi access point and web interface, with the mobile gateway and cloud tier funded by this round',
    'Recording-quality check takes about 145 seconds and noise reduction is not yet implemented; performance under field noise unquantified',
    'Advances in edge AI, MEMS sensors, and open respiratory sound datasets lower the development barrier',
    'Better-funded commercial digital stethoscopes may add comparable software features'],
  ['Legal',
    'Role-based access and de-identified research exports designed in from the start',
    'Must satisfy FDA registration (Republic Act No. 9711, 2009) and the Data Privacy Act (Republic Act No. 10173, 2012); IP ownership not yet formalized with the school',
    'Compliance built during development is cheaper than retrofitting it',
    'Reclassification to a higher device risk category would extend timeline and cost'],
  ['Environmental',
    'Rechargeable device and digital records reduce paper and disposables',
    'Electronic components require maintenance, repair, and end-of-life disposal',
    'Local 3D printing and repairable design extend device life and support local assembly',
    'Electronic waste and limited formal e-waste infrastructure in provincial areas'],
], [1100, 2065, 2065, 2065, 2065]));
add(new Paragraph({ spacing: { before: 120, after: 180 },
  children: [T('Note. ', { italics: true, size: 20 }),
             T('PESTLE = Political, Economic, Social, Technological, Legal, Environmental.', { size: 20 })] }));

add(P('Table 10 shows that Resondi’s position rests on cost and workflow integration rather than '
  + 'on acoustic performance alone, and that its principal constraints are regulatory and '
  + 'technical rather than commercial. The strongest opportunities follow from the Universal '
  + 'Health Care Act’s primary-care orientation and the underfunding of that level of care, while '
  + 'the most material threats are a possible reclassification to a higher device risk category '
  + 'and the entry of better-funded competitors into the same workflow niche.'));

add(SH('Risk register'));
add(P('Table 10 describes the environment the venture operates in. Table 11 states the risks the '
  + 'venture itself carries, with the response to each and the officer accountable for it. '
  + 'Likelihood and impact are graded High, Medium or Low on the eighteen-month programme '
  + 'horizon. The two risks graded High on both axes \u2014 classification performance and '
  + 'continuity after graduation \u2014 are the two the funding and the corporate structure are '
  + 'respectively designed to address.'));
add(...TCAP(11, 'Risk Register and Mitigation'));
add(TBL([
  ['Risk', 'Likelihood', 'Impact', 'Response and accountable officer'],
  ['Classification performance remains weak after retraining on a patient-wise split',
   'High', 'High',
   'Baseline published before the largest spend; fixed test partition across all runs; product positioned as decision support with a practitioner confirmation gate, so clinical use does not depend on autonomous accuracy \u2014 CEO'],
  ['Team disperses after graduation and the venture stalls',
   'High', 'High',
   'SEC incorporation in Phase 1; shareholder and officer roles assigned at registration; documented handover of firmware, platform and model artefacts \u2014 CEO'],
  ['Ethics committee review delays the prospective evaluation',
   'Medium', 'High',
   'Submission prepared in Phase 1 and run in parallel with device refinement rather than after it; \u20b110,000 budgeted \u2014 COO'],
  ['Device is classified above Class A, requiring a CMDR rather than a CMDN',
   'Low', 'High',
   'Classification determination sought from the CDRRHR before the registration file is prepared; declared claim held to decision support \u2014 CEO'],
  ['Intellectual property ownership is not resolved with the school',
   'Medium', 'High',
   'Assignment agreement executed in Phase 1, before any commercial agreement is signed; \u20b13,000 budgeted \u2014 CEO'],
  ['Breach or loss of stored recordings, which are sensitive personal information',
   'Low', 'High',
   'Data Protection Officer designated from the first recording; encryption at rest and in transit; National Privacy Commission registration before the installed base reaches 1,000 individuals; statutory breach notification \u2014 CTO'],
  ['Local government procurement cycles miss the budget year',
   'High', 'Medium',
   'Education channel opens first and carries earliest revenue; donor-funded deployments bridge the gap; pipeline built a budget cycle ahead \u2014 CEO'],
  ['Device failure or drift in the field',
   'Medium', 'Medium',
   'One spare unit per cluster of five facilities; faulty unit swapped within five working days; annual calibration check; funded by the \u20b1250 monthly reserve \u2014 COO'],
  ['Cloud and storage cost per facility exceeds the \u20b1350 allowance as recordings accumulate',
   'Medium', 'Low',
   'Allowance funded for the first twelve commercial months from the cloud operation line; cost per facility reviewed at the end of the pilot and the subscription repriced at renewal \u2014 CTO'],
], [2600, 1150, 950, 4660]));

// ───────────────────────────────────────────── OPERATIONS PLAN
add(H('OPERATIONS PLAN'));
add(P('Resondi will deliver its smart stethoscope and mobile application through partnerships '
  + 'with hospitals, clinics, rural health units, and nursing and medical schools. The startup '
  + 'will manage device production and testing, application deployment, user onboarding, and '
  + 'technical support. Healthcare workers and patients will be trained to use the device and '
  + 'application for guided cardiopulmonary monitoring and rehabilitation support.'));
add(P('Implementation proceeds in six phases over eighteen months. Each phase has an exit '
  + 'criterion that must be met before the next is funded, so that a failure is discovered before it '
  + 'is funded further. Table 12 sets out the phases, the founder who owns each, their '
  + 'activities, and their exit outputs.'));
add(...TCAP(12, 'Six-Phase Implementation Plan Over Eighteen Months'));
add(TBL([
  ['Phase', 'Period', 'Owns / supports', 'Key activities', 'Output'],
  ['1. Clearance', 'Months 1–2', 'CEO / COO',
    'Register the company with the Securities and Exchange Commission; resolve dataset licensing for commercial use; confirm IP ownership; determine device classification under RA 9711; draft consent language permitting product development',
    'Written legal and regulatory position'],
  ['2. Evidence', 'Months 2–5', 'CEO / CTO',
    'Train and evaluate the classification model on a patient-wise split; establish honest baseline performance; quantify the gap between reference recordings and Resondi hardware',
    'Validated baseline performance report'],
  ['3. Quality and device data', 'Months 4–9', 'CEO / CTO',
    'Cut recording-quality assessment from about 145 seconds to a usable latency and add noise reduction; ethics approval; collect and clinically label cardiopulmonary recordings on Resondi hardware; fine-tune on device-matched data',
    'Fast quality-assessment module; local labelled dataset; improved model'],
  ['4. Pilot', 'Months 8–13', 'COO / CTO',
    'Deploy units to partner rural health units, clinics, and schools; train health workers; collect usability and reliability data; iterate on the application',
    'Field-tested platform; usage evidence'],
  ['5. Validation', 'Months 12–16', 'COO / CEO',
    'Prospective evaluation against practitioner reference assessment; measure agreement, recording quality, and performance under field noise conditions',
    'Clinical validation results'],
  ['6. Registration and launch', 'Months 15–18', 'CEO / COO',
    'Regulatory submission matched to the declared claim; establish quality management system; begin commercial sale through education and LGU channels',
    'Registered product; first paying customers'],
], [1500, 1000, 1760, 3250, 1850]));
add(SH('Delivery and support'));
add(P('Devices are assembled in-house during the pilot phase and transitioned to a contract '
  + 'assembler once volume justifies it. Each deployment includes an on-site training session for '
  + 'health workers, printed quick-reference materials for guided auscultation, and a replacement '
  + 'unit held in reserve per cluster of facilities. Platform support is provided remotely, with '
  + 'escalation to the development team for device faults.'));

add(SH('Team and phase ownership'));
add(P('Resondi is founded by three senior high school students — Ahnycca Krish N. Malimban, '
  + 'Hared Ray Cabrera and Jarred Paul Llacuna — working under a research adviser from the '
  + 'PPCNSHS research programme. Those three are the registered startup team and are marked '
  + 'in Figure 10, where each holds an officer title: Ahnycca as Chief Executive Officer, '
  + 'Hared as Chief Technology Officer, and Jarred Paul as Chief Operating Officer. The plan '
  + 'is executed by the three of them, reporting to an Advisory Board. Figure 10 sets out the '
  + 'structure; the founder who owns and the founder who supports each phase are given in '
  + 'Table 12. The Advisory Board comprises '
  + 'the research adviser, the consulting clinicians, the electronics engineer, and the '
  + 'practitioner reviewer network. It reviews, endorses and approves; it holds no phase '
  + 'and no delivery responsibility, so that accountability for every exit criterion rests '
  + 'with a named founder.'));
add(...FIG(10, 'Organizational Structure',
  FIGS + 'fig9_org.png', 580, 432));
add(P('The three officers divide the work by the kind of risk each carries rather than by '
  + 'discipline alone. The CEO holds data and model operations directly, because the labelled '
  + 'corpus and the retraining pipeline are the assets the funding is primarily sought to build, '
  + 'together with the product claim, the regulatory file, and sales and partnerships. The CTO '
  + 'owns the mobile application, the cloud tier, information security and the quality '
  + 'assurance that precedes any release to a facility, and is the designated Data Protection '
  + 'Officer. The COO owns the physical device through refinement, assembly, the transition to '
  + 'contract manufacture and service in the field, runs the clinical relationships, ethics '
  + 'submission and validation studies, and keeps the finances.'));
add(P('Each phase has one owning founder and one supporting founder, so that responsibility '
  + 'for an exit criterion is never shared. The CEO owns Phases 1, 2, 3 and 6: clearance and '
  + 'registration because the regulatory file and the declared claim sit with the CEO, and the '
  + 'two evidence phases because both turn on model performance. The COO owns the pilot in '
  + 'Phase 4, which is field placement and training, and the prospective evaluation in Phase 5, '
  + 'so that the evaluation is run by a founder who did not build the model being evaluated, '
  + 'with reference assessment by the consulting clinicians on the Advisory Board.'));

add(SH('Operating functions and service commitments'));
add(P('The same three officers run the business once commercial operation begins in month 15. '
  + 'The titles in Figure 10 are operating roles, not programme roles, so that the structure '
  + 'does not have to be rebuilt at launch. Table 13 states what each function covers and the '
  + 'commitment attached to it. Two of these commitments are funded explicitly: device '
  + 'maintenance and replacement are carried by the ₱250 per facility per month reserve inside '
  + 'the ₱1,500 subscription, and platform operation by the ₱350 per facility per month '
  + 'allowance, both set out in Table 5.'));
add(...TCAP(13, 'Operating Functions, Owners and Service Commitments'));
add(TBL([
  ['Function', 'Owner', 'Scope and commitment'],
  ['Executive, data and model operations',
   'Ahnycca Krish N. Malimban, CEO',
   'Dataset curation and labelling pipeline, retraining runs, and performance monitoring after each model update; investor reporting against the ₱500,000 recovery schedule; signatory on every regulatory submission'],
  ['Platform operations',
   'Hared Ray Cabrera, CTO',
   'Cloud hosting, backup and restore, release management, and Data Privacy Act compliance for stored recordings. Backup restored within 24 hours of a request'],
  ['Application development',
   'Hared Ray Cabrera, CTO',
   'Mobile application builds, offline capture and synchronisation, defect resolution. Security review before each release to a facility'],
  ['Product and AI',
   'Ahnycca Krish N. Malimban, CEO',
   'The deployed MFCC classifier and its planned feature-fusion successor, and the specification of what the product claims and does not claim'],
  ['Production and supply chain',
   'Jarred Paul Llacuna, COO',
   'Component sourcing, in-house assembly during the pilot, transition to a contract assembler above 100 units, and a functional test on every unit before dispatch'],
  ['Device maintenance and field service',
   'Jarred Paul Llacuna, COO',
   'Repair, recalibration and replacement. One spare unit held per cluster of five facilities; a faulty unit is swapped within five working days and returned for repair; calibration checked annually. Funded by the ₱250 monthly reserve'],
  ['Clinical affairs and validation',
   'Jarred Paul Llacuna, COO',
   'Practitioner reviewer network, clinical content approval, validation studies, and on-site clinician training at each deployment'],
  ['Regulatory and compliance',
   'Ahnycca Krish N. Malimban, CEO',
   'FDA device registration and renewal, quality management system records, and the standing regulatory position on the declared claim'],
  ['Data protection',
   'Hared Ray Cabrera, CTO, designated Data Protection Officer',
   'Designation under the Data Privacy Act, which applies from the first recording and not at a threshold; National Privacy Commission registration before the installed base holds sensitive personal information of 1,000 individuals; consent records and data subject requests'],
  ['Information security and incident response',
   'Hared Ray Cabrera, CTO',
   'Access control, encryption of recordings at rest and in transit, and breach notification to the Commission and to affected individuals inside the statutory window'],
  ['Sales, marketing and customer success',
   'Ahnycca Krish N. Malimban, CEO',
   'LGU and DOH procurement, school licences, distributor agreements, and the first-line support desk, with response to a support request within one business day. Also owns the ₱15,000 deployment and marketing line: product website, demonstration materials, expo presence and professional channels'],
  ['Finance, people and administration',
   'Jarred Paul Llacuna, COO',
   'Invoicing and collections, procurement, and monthly contribution reporting. Also recruitment, employment contracts, onboarding and payroll once salaried roles begin, and the statutory filings a registered company carries'],
], [2180, 2180, 5000]));
add(SH('Continuity and governance'));
add(P('The research ends; the company does not. Three mechanisms carry Resondi past the '
  + 'point at which it stops being a school project. The first is a legal entity: the '
  + '₱500,000 is received by a company registered with the Securities and Exchange '
  + 'Commission, which Phase 1 establishes alongside the resolution of intellectual property '
  + 'ownership with the school. After registration the company exists independently of '
  + 'whether any founder is still enrolled, and it, rather than an individual, holds the '
  + 'licences, the contracts and the registration file.'));
add(P('The second is that maintenance is funded from operations rather than from the grant. '
  + 'Device service is carried by the ₱250 per facility per month replacement reserve and '
  + 'platform operation by the ₱350 allowance, both inside the ₱1,500 subscription. From '
  + 'month 15 these obligations are met from recurring revenue, so support does not depend '
  + 'on a further raise.'));
add(P('The third is that every function has a named owner, and the functions that can be '
  + 'performed remotely — platform, data and model operations, regulatory, finance — travel '
  + 'with the founders when they leave for university. The two that require presence in '
  + 'Palawan, field service and deployment training, are the first salaried hires, triggered '
  + 'at twenty-five facilities and at fifty respectively. Until those hires are made the '
  + 'installed base is deliberately capped at what the team can physically support: the '
  + 'constraint on deployment pace is service capacity, not demand.'));
add(P('One commitment follows from the architecture and is made explicitly. If the company '
  + 'ceases to operate, a deployed device does not stop working: it continues to record and '
  + 'to file to MicroSD, because capture does not depend on the platform. What would stop is '
  + 'AI-assisted analysis and longitudinal comparison. The stored recordings belong to the '
  + 'facility and the patient rather than to the company, and would be returned to the '
  + 'facility in a portable format. That is the floor the system is designed to, and it is '
  + 'the reason connectivity and the platform are treated as conveniences rather than as '
  + 'preconditions throughout this document.'));

add(P('Three functions are deliberately not staffed internally. Volume assembly moves to a '
  + 'contract assembler once unit demand passes roughly one hundred, because in-house assembly '
  + 'does not scale past the pilot. Channel reach beyond MIMAROPA runs through medical '
  + 'equipment distributors rather than a direct sales team. Legal work beyond routine '
  + 'contracting is bought in, under the ₱4,000 legal consultation line. The first salaried '
  + 'hires, funded from operating contribution rather than from the seed, would be a field '
  + 'service technician once the installed base passes roughly twenty-five facilities, and a '
  + 'support officer once it passes fifty.'));

// ───────────────────────────────────────────── FINANCIAL
add(H('FINANCIAL REQUIREMENT'));
add(P('Resondi requires ₱500,000 to advance from working prototype to validated, deployable '
  + 'product. Two commitments drive the figure. The first is evidence: fifteen paired recordings '
  + 'cannot establish performance, and clinical validation is scaled accordingly. The second is '
  + 'the technical gap the prototype has not yet closed — a recording-quality check fast enough '
  + 'for routine use, noise reduction, and a corpus of Filipino recordings the model has never seen. The '
  + 'allocation also carries three lines a programme of this length cannot responsibly run '
  + 'without: cloud operation beyond the '
  + 'development period, intellectual property registration, and an unallocated contingency at '
  + 'ten percent. Figure 11 and Table 14 set out the allocation across ten categories.'));
add(...FIG(11, 'Allocation of the ₱500,000 Requirement',
  FIGS + 'Figure-11-Allocation-500k.png', 580, 361));
add(...TCAP(14, 'Allocation of the ₱500,000 Financial Requirement'));
add(TBL([
  ['Category', 'Share', 'Amount'],
  ['Clinical validation', '24.00%', '₱120,000'],
  ['AI development', '20.40%', '₱102,000'],
  ['Contingency', '10.00%', '₱50,000'],
  ['Cloud infrastructure and operation', '9.60%', '₱48,000'],
  ['Hardware refinement', '8.40%', '₱42,000'],
  ['Production working capital', '8.00%', '₱40,000'],
  ['Mobile application', '7.60%', '₱38,000'],
  ['Intellectual property and registration', '5.00%', '₱25,000'],
  ['Documentation and compliance', '4.00%', '₱20,000'],
  ['Deployment and marketing', '3.00%', '₱15,000'],
  ['TOTAL', '100.00%', '₱500,000'],
], [5000, 2000, 2360], true));

add(SH('Detailed breakdown'));
add(P('Table 15 gives the line-item breakdown within each category. Shares are stated at '
  + 'category level, as in Table 14; line items carry their peso amount alone, so that the '
  + 'column sums exactly rather than drifting on rounding.'));
add(...TCAP(15, 'Detailed Line-Item Breakdown of the Financial Requirement'));
const DET = [['Line item', 'Cost', '% of total']];
const push = (name, cost, pct) => DET.push([name, cost, pct]);
push('CLINICAL VALIDATION', '₱120,000', '24.00%');
push('   Prospective evaluation at pilot sites, target 300 paired recordings', '₱38,000', '7.60%');
push('   Clinician honoraria for reference assessment', '₱24,000', '4.80%');
push('   Transportation and field operations across Palawan sites', '₱22,000', '4.40%');
push('   Ethics committee review and protocol submission', '₱10,000', '2.00%');
push('   Data collection activities', '₱10,000', '2.00%');
push('   Validation materials and forms', '₱8,000', '1.60%');
push('   Participant materials and printing', '₱8,000', '1.60%');
push('AI DEVELOPMENT', '₱102,000', '20.40%');
push('   Filipino recording collection and clinical annotation', '₱46,000', '9.20%');
push('   Noise reduction and faster quality assessment', '₱20,000', '4.00%');
push('   GPU cloud computing for model training', '₱16,000', '3.20%');
push('   Model integration to mobile platform', '₱8,000', '1.60%');
push('   Performance evaluation on a patient-wise split', '₱7,000', '1.40%');
push('   Feature-fusion training and ablation against the baseline', '₱5,000', '1.00%');
push('CONTINGENCY', '₱50,000', '10.00%');
push('   Unallocated reserve, released only against a documented overrun', '₱50,000', '10.00%');
push('CLOUD INFRASTRUCTURE AND OPERATION', '₱48,000', '9.60%');
push('   Cloud operation, first 12 months of commercial service', '₱18,000', '3.60%');
push('   Cloud server hosting across the 18-month programme', '₱15,000', '3.00%');
push('   Secure database storage', '₱5,000', '1.00%');
push('   Data backup services', '₱5,000', '1.00%');
push('   Domain and web services', '₱3,000', '0.60%');
push('   API services and maintenance', '₱2,000', '0.40%');
push('HARDWARE REFINEMENT', '₱42,000', '8.40%');
push('   High-sensitivity microphones and acoustic testing', '₱10,000', '2.00%');
push('   PCB revision and fabrication', '₱8,000', '1.60%');
push('   Casing design and print iteration', '₱8,000', '1.60%');
push('   ESP32 and components for iteration units', '₱8,000', '1.60%');
push('   Batteries and charging modules', '₱4,000', '0.80%');
push('   Spare parts and test failures', '₱4,000', '0.80%');
push('PRODUCTION WORKING CAPITAL', '₱40,000', '8.00%');
push('   Components for the first ten saleable units', '₱34,000', '6.80%');
push('   Assembly, calibration and quality check', '₱4,000', '0.80%');
push('   Packaging and delivery to facilities', '₱2,000', '0.40%');
push('MOBILE APPLICATION', '₱38,000', '7.60%');
push('   Practitioner dashboard and review workflow', '₱9,000', '1.80%');
push('   Role-based access control and audit logging', '₱8,000', '1.60%');
push('   Offline capture and synchronisation', '₱7,000', '1.40%');
push('   Longitudinal comparison views', '₱7,000', '1.40%');
push('   Testing, debugging and security review', '₱7,000', '1.40%');
push('INTELLECTUAL PROPERTY AND REGISTRATION', '₱25,000', '5.00%');
push('   IPOPHL trademark registration for the Resondi mark', '₱9,000', '1.80%');
push('   Utility model or industrial design filing', '₱8,000', '1.60%');
push('   SEC incorporation and initial statutory filings', '₱5,000', '1.00%');
push('   Intellectual property assignment agreement with the school', '₱3,000', '0.60%');
push('DOCUMENTATION AND COMPLIANCE', '₱20,000', '4.00%');
push('   FDA device notification and quality system documentation', '₱5,000', '1.00%');
push('   Research documentation', '₱4,000', '0.80%');
push('   Legal consultation', '₱4,000', '0.80%');
push('   Data privacy compliance', '₱3,000', '0.60%');
push('   Printing and technical reports', '₱2,000', '0.40%');
push('   Administrative expenses', '₱2,000', '0.40%');
push('DEPLOYMENT AND MARKETING', '₱15,000', '3.00%');
push('   Demonstration materials', '₱5,000', '1.00%');
push('   Healthcare institution outreach', '₱4,000', '0.80%');
push('   Promotional materials', '₱3,000', '0.60%');
push('   Exhibits and product presentations', '₱3,000', '0.60%');
push('TOTAL', '₱500,000', '100.00%');

// Shares live on the category rows only. Line-item percentages round to two places
// and so cannot be made to sum to their category exactly; the peso column does.
DET.forEach((r, i) => { if (i > 0 && r[0].startsWith('   ')) r[2] = ''; });

const headerRows = new Set();
DET.forEach((r, i) => { if (i > 0 && !r[0].startsWith('   ')) headerRows.add(i); });
add(new Table({
  columnWidths: [5400, 1900, 2060],
  width: { size: CONTENT, type: WidthType.DXA },
  rows: DET.map((row, r) => new TableRow({
    tableHeader: r === 0,
    children: row.map((t, i) => new TableCell({
      width: { size: [5400, 1900, 2060][i], type: WidthType.DXA },
      shading: (r === 0 || headerRows.has(r))
        ? { type: ShadingType.CLEAR, fill: r === 0 ? 'D9D9D9' : 'F2F2F2', color: 'auto' } : undefined,
      margins: { top: 50, bottom: 50, left: 90, right: 90 },
      children: [new Paragraph({ spacing: { after: 0, line: 220 },
        children: [Tt(String(t), { bold: r === 0 || headerRows.has(r) })] })],
    })),
  })),
}));

add(SH('Note on hardware and production costs'));
add(P('Three distinct figures appear in this document and should not be confused. The ₱42,000 '
  + 'hardware refinement allocation is research and development: it buys roughly three '
  + 'design-iteration units at about ₱14,000 each, a figure that reflects single-quantity retail '
  + 'pricing, failed casing prints, board revisions, and test failures rather than production '
  + 'economics. What it yields is a frozen design, not saleable stock. The ₱40,000 production '
  + 'working capital allocation is separate, and buys the first batch of ten saleable units at '
  + 'approximately ₱4,000 each fully loaded: ₱3,400 of components once the design is frozen — '
  + 'the ₱2,735 bill of materials plus battery protection, charging and the production '
  + 'allowance — together with assembly, calibration, functional test and packaging. '
  + 'The fully loaded figure, not the component cost '
  + 'alone, is what the ₱8,000 price is set against. '
  + 'That figure falls toward ₱3,000 at one hundred units with silicone vacuum-cast '
  + 'enclosures, batch PCB fabrication, and bulk component pricing. Injection moulding is not '
  + 'assumed at that volume, since the tooling would not amortise over a hundred units. '
  + 'The ₱8,000 selling price is set against the marginal '
  + 'cost, not against the refinement cost. Beyond the first batch the cycle is self-funding: each '
  + 'unit returns its ₱4,000 of cost together with ₱4,000 of margin, and later batches are built '
  + 'against confirmed purchase orders rather than drawn from the seed.'));
add(P('Two parts figures sit beneath these and should be read alongside them rather than against '
  + 'them. The prototype that was built and evaluated in the research paper cost ₱2,094.47 in '
  + 'materials (Malimban, 2026). The bill of materials for the VER 2.0 build described in '
  + 'Table 1 estimates ₱2,735.00 for one unit at Philippine retail prices (Team Wheezards, 2026); '
  + 'it is higher because that build replaces the power bank with a 10,000 mAh battery and boost '
  + 'converter and reads the microphone digitally without a separate preamplifier. Both are '
  + 'component lists for a bench build, and the bill of materials excludes by its own note the '
  + 'battery protection and charging circuit, together with assembly labour, functional test, '
  + 'packaging, shipping, and the parts consumed during iteration. The ₱4,000 marginal figure '
  + 'used throughout this document is the all-in cost of a unit a facility can be sold, and is '
  + 'deliberately the most conservative of the three. The gap between them is not a '
  + 'discrepancy; it is the difference between what a prototype costs in parts and what a '
  + 'product costs to produce.'));

add(SH('What the requirement does not include'));
add(P('The ₱500,000 covers cash costs only. No founder or team salary is drawn against it, and '
  + 'no stipend is budgeted for the eighteen months of development; the team contributes its '
  + 'time. School laboratory equipment already available to the team is likewise excluded. The '
  + 'requirement is therefore small relative to the scope of work, and deliberately so: it is '
  + 'what the programme costs in money, not what it would cost to commission.'));
add(P('Compensation is deferred rather than absent, and the point at which it begins is '
  + 'stated so that it is not discovered later. No role is salaried during the development '
  + 'programme. The first paid positions are funded from operating contribution and not from '
  + 'the seed: a field service technician once the installed base passes roughly twenty-five '
  + 'facilities, and a support officer once it passes fifty. Until those thresholds are '
  + 'reached, the service commitments in Table 13 are met by the team without compensation, and '
  + 'the payroll obligations assigned to Finance in that table begin only when the first '
  + 'salaried role does. A model that assumes indefinite unpaid work would not be credible, '
  + 'and the thresholds are set where contribution can actually carry the cost.'));
add(P('The requirement carries an explicit '
  + 'contingency of ₱50,000, ten percent of the total, held unallocated and released only '
  + 'against a documented overrun. Where contingency is insufficient the response remains to '
  + 'extend the schedule rather than to raise a second round, since every phase except clinical '
  + 'validation can absorb delay without additional cost.'));

add(SH('Return on the requirement'));
add(P('The requirement is recovered from operations rather than from a second raise. '
  + 'Commercial Year 1 cash contribution of ₱175,900 returns a little over a '
  + 'third of the seed, and the crossover falls in the second commercial year, once twenty-five '
  + 'facilities are paying a subscription against no further development commitment. Modelled '
  + 'month by month, with the ten first-year facilities coming online across that year and the '
  + 'first production batch funded from the production working capital allocation, cumulative '
  + 'contribution passes ₱500,000 in the twenty-first month of commercial '
  + 'operation, as Figure 12 shows. A smaller requirement would be recovered sooner — at ₱300,000 the same model '
  + 'crosses in the sixteenth month — and the five additional months are the '
  + 'price of funding the evidence base properly rather than deferring it. That trade is '
  + 'stated rather than absorbed silently.'));
add(...FIG(12, 'Cumulative Cash Contribution Against the ₱500,000 Seed',
  FIGS + 'Figure-12-Cumulative-Recovery.png', 580, 397));
add(P('Two anchors should not be confused. Twenty-one months is counted from first sale, which '
  + 'is month 15 of the implementation plan and the first month of commercial operation; measured '
  + 'from the date of funding the same point falls at month 35. A twelve-month payback is not '
  + 'claimed under either anchor. Local '
  + 'government procurement cycles are annual, registration must precede clinical sale, and '
  + 'subscription revenue accumulates slowly by design.'));
add(P('The investor return is slower still, and the arithmetic is given rather than implied. '
  + 'A forty percent share of net earnings repays ₱500,000 only once cumulative net earnings '
  + 'reach ₱1,250,000. Cumulative contribution reaches ₱602,800 by the end of commercial '
  + 'Year 2 and ₱1,488,500 by the end of Year 3, so repayment falls in the third commercial '
  + 'year and not the second. Where in that year depends on operating overhead, which is not '
  + 'yet costed because no role is salaried during the development programme. Table 16 states '
  + 'the repayment month across a band of overhead assumptions rather than asserting a single '
  + 'figure the model cannot support.'));
add(...TCAP(16, 'Investor Repayment Against Operating Overhead'));
add(TBL([
  ['Operating overhead as a share of contribution', 'Repaid in commercial month', 'Measured from funding', 'Share of net required to repay by month 36'],
  ['0 percent', 'Month 33', 'Month 47', '34 percent'],
  ['15 percent', 'Month 36', 'Month 50', '40 percent'],
  ['25 percent', 'Beyond month 36', '—', '45 percent'],
  ['35 percent', 'Beyond month 36', '—', '52 percent'],
], [3600, 2400, 2200, 2160]));
add(new Paragraph({ spacing: { before: 120, after: 180 },
  children: [T('Note. ', { italics: true, size: 20 }),
             T('Repayment at a forty percent share of net earnings. The final column gives the '
               + 'share that would instead be required to return the full ₱500,000 by the end of '
               + 'commercial Year 3 at each overhead level.', { size: 20 })] }));
add(P('Two consequences follow and are stated rather than left to be discovered. The first is '
  + 'that a forty percent share returns the seed inside the projected horizon only if overhead '
  + 'stays below roughly fifteen percent of contribution, which is plausible while the team is '
  + 'unsalaried but not once the field technician and support officer are hired. The second is '
  + 'that raising the share to about forty-five percent returns the seed by month 36 under a '
  + 'twenty-five percent overhead assumption. The venture is open to either structure, and to '
  + 'pricing the equity stake instead, but it will not claim a repayment date the revenue model '
  + 'does not produce.'));

add(SH('Use of funds against milestones'));
add(P('Funding is released against the phase gates in the Operations Plan rather than drawn '
  + 'evenly. The first tranche covers clearance and evidence, which together cost little but '
  + 'determine whether the remainder should be spent at all. The largest commitment, AI '
  + 'development, is made only after the baseline performance report establishes what the current '
  + 'model actually achieves on a patient-wise split. Within that allocation, a faster '
  + 'recording-quality check and noise reduction are the first deliverables, since they are '
  + 'the capability gap between the present prototype and a device that can be trusted in a noisy '
  + 'rural health unit. This sequencing limits downside exposure should an early phase gate fail.'));

// ────────── THE ASK
add(H('THE ASK'));
add(P('Resondi asks for ₱500,000 to take a working prototype to a validated, registered and '
  + 'deployable product over eighteen months. Just under half of that — ₱222,000 — buys the '
  + 'two things the prototype most lacks: evidence at a sample size that can support a '
  + 'performance claim, and a corpus of Filipino recordings the model has never heard. The '
  + 'remainder funds the device refinement, the platform, the regulatory file, the first batch '
  + 'of saleable units, and a ten percent contingency held against documented overrun.'));
add(P('What the funder receives is set out in full above: forty percent of net earnings until '
  + 'the ₱500,000 is returned, together with an agreed equity stake in a company registered '
  + 'with the Securities and Exchange Commission during the first two months. The business '
  + 'recovers the seed from operations in the twenty-first month of commercial trading, which '
  + 'is month 35 from funding; the investor share returns it during the third commercial year, '
  + 'on the overhead assumptions in Table 16. No twelve-month payback is claimed under any '
  + 'anchor.'));
add(P('What this document does not claim is equally deliberate. Fifteen paired recordings '
  + 'cannot establish classification accuracy, and none is asserted. The system screens '
  + 'recordings for quality before analysis, but too slowly to do so on every capture, and that '
  + 'gap is the first thing the funding closes. The training corpus contains no Filipino recordings. These are the reasons for the '
  + 'request rather than objections to it, and the team would rather a funder read them here '
  + 'than discover them later.'));

// ────────── REFERENCES
add(H('REFERENCES'));
const REFS = [
  '3M. (2025). Littmann CORE digital stethoscope (Model 8480) [Product listing]. https://mdmaxx.com/products/3m-8480-littmann-core-digital-stethoscope',
  'Arts, L., Lim, E. H. T., van de Ven, P. M., Heunks, L., & Tuinman, P. R. (2020). The diagnostic accuracy of lung auscultation in adult patients with acute pulmonary pathologies: A meta-analysis. Scientific Reports, 10, 7347. https://doi.org/10.1038/s41598-020-64405-6',
  'Bohadana, A., Izbicki, G., & Kraman, S. S. (2014). Fundamentals of lung auscultation. The New England Journal of Medicine, 370(8), 744–751. https://doi.org/10.1056/NEJMra1302901',
  'Department of Health. (2020). Philippine health facility development plan 2020–2040. Republic of the Philippines.',
  'Department of Health. (2025). National health facility registry. https://nhfr.doh.gov.ph',
  'Hossain, M. A., et al. (2025). Delivering remote pulmonary rehabilitation in Bangladesh: A mixed-method feasibility study. https://pmc.ncbi.nlm.nih.gov/articles/PMC11825123',
  'Hsu, F.-S., Huang, S.-R., Huang, C.-W., et al. (2021). Benchmarking of eight recurrent neural network variants for breath phase and adventitious sound detection on a self-developed open-access lung sound database—HF_Lung_V1. PLOS ONE, 16(7), e0254134. https://doi.org/10.1371/journal.pone.0254134',
  'Huang, D.-M., Huang, J., Qiao, K., Zhong, N.-S., Lu, H.-Z., & Wang, W.-J. (2023). Deep learning-based lung sound analysis for intelligent stethoscope. Military Medical Research, 10(1), 44. https://doi.org/10.1186/s40779-023-00479-3',
  'Kim, Y., Kim, K. B., Leem, A. Y., Kim, K., & Lee, S. H. (2025). Enhanced respiratory sound classification using deep learning and multi-channel auscultation. Journal of Clinical Medicine, 14(15), 5437. https://doi.org/10.3390/jcm14155437',
  'Lahham, A., & Holland, A. E. (2021). The need for expanding pulmonary rehabilitation services. Life, 11(11), 1236. https://doi.org/10.3390/life11111236',
  'Leng, S., Tan, R. S., Chai, K. T. C., Wang, C., Ghista, D., & Zhong, L. (2015). The electronic stethoscope. BioMedical Engineering OnLine, 14, 66. https://doi.org/10.1186/s12938-015-0056-y',
  'Malimban, A. K. N. (2026). Resondi: A CNN-assisted auscultation instrument for lung sound monitoring, longitudinal tracking, and rehabilitation support-system [Unpublished research paper]. Puerto Princesa City National Science High School.',
  'Oliveira, J., Renna, F., Costa, P. D., Nogueira, M., Oliveira, C., Ferreira, C., Jorge, A., Mattos, S., Hatem, T., Tavares, T., Elola, A., Rad, A. B., Sameni, R., Clifford, G. D., & Coimbra, M. T. (2022). The CirCor DigiScope dataset: From murmur detection to murmur classification. IEEE Journal of Biomedical and Health Informatics, 26(6), 2524\u20132535. https://doi.org/10.1109/JBHI.2021.3137048',
  'Park, D. Y., et al. (2025). Artificial intelligence models for pediatric lung sound analysis: Systematic review and meta-analysis. Journal of Medical Internet Research, 27, e66491. https://doi.org/10.2196/66491',
  'Philippine Statistics Authority. (2026, January 30). Registered deaths in the Philippines, 2024 (data as of 30 September 2025; not adjusted for under-registration). https://psa.gov.ph/content/registered-deaths-philippines-2024',
  'Republic Act No. 9711. (2009). Food and Drug Administration Act of 2009. Republic of the Philippines.',
  'Republic Act No. 10173. (2012). Data Privacy Act of 2012. Republic of the Philippines.',
  'Republic Act No. 11223. (2019). Universal Health Care Act. Republic of the Philippines.',
  'Rocha, B. M., Filos, D., Mendes, L., Serbes, G., Ulukaya, S., Kahya, Y. P., Jakovljevic, N., Turukalo, T. L., Vogiatzis, I. M., Perantoni, E., Kaimakamis, E., Natsiavas, P., Oliveira, A., Jácome, C., Marques, A., Maglaveras, N., Paiva, R. P., Chouvarda, I., & de Carvalho, P. (2019). An open access database for the evaluation of respiratory sound classification algorithms. Physiological Measurement, 40(3), 035001. https://doi.org/10.1088/1361-6579/ab03ea',
  'Shkarupylo, V., et al. (2024). Intelligent digital stethoscope for neural network analysis of auscultatory signals: A review of sensors, architectures and algorithms. https://science.lpnu.ua/node/43249',
  'Team Wheezards. (2026). Bill of materials (BOM): Resondi intelligent respiratory auscultation system, one prototype unit [Unpublished document]. Puerto Princesa City National Science High School.',
  'Tariq, Z., Shah, S. K., & Lee, Y. (2022). Feature-based fusion using CNN for lung and heart sound classification. Sensors, 22(4), 1521. https://doi.org/10.3390/s22041521',
  'United Nations. (2015). Transforming our world: The 2030 agenda for sustainable development (A/RES/70/1).',
];
REFS.forEach((r) => add(new Paragraph({
  spacing: { after: 140, line: 276 },
  indent: { left: 720, hanging: 720 },
  alignment: AlignmentType.LEFT,
  children: [T(r, { size: 22 })],
})));

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: SZ } } } },
  sections: (() => {
    const PORTRAIT = { page: { size: { width: 12240, height: 15840 },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } };
    // Landscape page for the business model canvas: 11 x 8.5 in, 0.5 in margins.
    const LANDSCAPE = { page: { size: { width: 12240, height: 15840,
      orientation: PageOrientation.LANDSCAPE },
      margin: { top: 720, right: 720, bottom: 720, left: 720 } } };
    const out = []; let cur = { properties: PORTRAIT, children: [] };
    for (const el of c) {
      if (el && el.__section) {
        if (cur.children.length) out.push(cur);
        cur = { properties: el.__section === 'landscape' ? LANDSCAPE : PORTRAIT, children: [] };
      } else cur.children.push(el);
    }
    if (cur.children.length) out.push(cur);
    return out;
  })(),
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(require('path').join(__dirname, '..', '..', 'deliverables', 'Resondi-Concept-Note-FINAL.docx'), b);
  console.log('written');
});
