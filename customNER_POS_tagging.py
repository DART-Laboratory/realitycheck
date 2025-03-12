# -*- coding: utf-8 -*-
import spacy
import random
from spacy.util import minibatch, compounding
from spacy.training import Example
import re
import nltk
from nltk.corpus import wordnet
import os
from nltk.stem.wordnet import WordNetLemmatizer
import pyinflect

nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('punkt')

# Define the training data and test data
TRAIN_DATA = [
    (
        "Loaded (source = DOWNLOAD): https://m.apkpure.com/fulldive-vr-virtual-reality/in.fulldive.shell",
        {"entities": [
            (28, 95, "URL")
        ]}
    ),
    (
        "[curlhttpclient] Executing HTTP request: https://graph.oculus.com/v1.20/me/friends, source_app_id: 704069629944399, Method=GET }",
        {"entities": [
            (41,82,"URL")
        ]}
    ),
    (
        "START u0 {act=android.intent.action.SEND dat=content://com.igalia.wolvic.provider/external_files/Android/data/com.igalia.wolvic/files/Download/com.apkpure.aegon-1011715.apk flg=0x10810401} from uid 10066",
        {"entities": [
            (41,172,"FILEPATH")
        ]}
    ),
    (
        "START u0 {act=android.intent.action.VIEW dat=content://com.igalia.wolvic.provider/external_files/Android/data/com.igalia.wolvic/files/Download/com.apkpure.aegon-1011715.apk flg=0x10810401} from uid 10066",
        {"entities": [
            (41,172,"FILEPATH_OR_URL")
        ]}
    ),
    (
        'START u0 {act=android.intent.action.VIEW dat=http://developer.android.com/... flg=0x10000000 cmp=com.oculus.os.vrbrowserlauncher/.MainActivity} from uid 2000',
        {'entities': [
            (41, 74, 'URL')
        ]}
    ),
    (
        'Background execution not allowed: receiving Intent { act=android.intent.action.PACKAGE_ADDED dat=package:com.oculus.ovrmonitormetricsservice flg=0x4000010 (has extras) } to com.android.packageinstaller/.PackageInstalledReceiver\r',
        {'entities': [
            (105, 140, 'PACKAGE_NAME')
        ]}
    ),
    (
        'START u0 {act=android.intent.action.MAIN cat=[android.intent.category.LAUNCHER] flg=0x10010000 pkg=com.oculus.vrshell cmp=com.oculus.vrshell/.MainActivity (has extras)} from uid 10025\r',
        {'entities': [
            (95, 154, 'PACKAGE_NAME')
        ]}
    ),
    (
        'Wrote bytes to file at /data/user/0/com.oculus.systemux/cache/library/apps\r',
        {'entities': [
            (23, 74, 'FILEPATH')
        ]}
    ),
    (
        "Loading file: 'vr_controller_oculusquest_left.obj'\r",
        {'entities': [
            (14, 50, 'FILEPATH')
        ]}
    ),
    (
        'RuntimeIPCServerMgr: RegisterClient: Client: com.oculus.os.vrusb:com.oculus.os.vrusb:1873, Server: com.oculus.systemdriver:com.oculus.vrruntimeservice (gkcache)', 
        {'entities': [
            (99, 150, 'PROCESS_NAME')
            ]}
    ),
    (
        'Read cached file from cache at /data/user/0/com.oculus.systemux/cache/library/apps\r',
        {'entities': [
            (31, 82, 'FILEPATH')
        ]}
    ),
    (
        'Start proc 4059:oculus.platform/1000 for service {oculus.platform/oculus.internal.telemetry.TelemetryEventSchemaFetchJobService}\r',
        {'entities': [
            (16, 36, 'PROCESS_NAME')
        ]}
    ),
    (
        'Binder  : \tat oculus.internal.DumpsysProxyService$ClientInfo.dumpState(DumpsysProxyService.java:162)', 
        {'entities': [
            (30, 60, 'PROCESS_NAME')
            ]}
    ),
    (
        'Start proc 4440:com.oculus.browser:sandboxed_process0:org.chromium.content.app.SandboxedProcessService0:1/u0ai1 for  {com.oculus.browser/org.chromium.content.app.SandboxedProcessService0:1}\r',
        {'entities': [
            (16, 34, 'PROCESS_NAME')
        ]}
    ),
    (
        'START u0 {act=android.intent.action.VIEW dat=content://com.igalia.wolvic.provider/external_files/Android/data/com.igalia.wolvic/files/Download/com.apkpure.aegon-1011715.apk typ=application/vnd.android.package-archive flg=0x10810401 cmp=com.android.packageinstaller/.InstallStart} from uid 10066',
        {'entities': [
            (41, 172, 'FILEPATH')
            ]}
    ),
    (
        'Process org.mozilla.vrbrowser (pid 7431) has died: fore TRNB',
        {'entities': [
            (8, 29, 'PROCESS_NAME')
        ]}
    ),
    (
        'Process com.oculus.vrshell (pid 2251) has died: fore SVC ',
        {'entities': [
            (8, 26, 'PROCESS_NAME')
        ]}
    ),
    (
        'User clicked app tile to launch Meta Quest Browser',
        {'entities': [
            (32, 50, 'PROCESS_NAME')
        ]}
    ),
    (
        'User clicked app tile to launch Firefox Reality',
        {'entities': [
            (32, 47, 'PROCESS_NAME')
        ]}
    ),
    (
        'AnytimeUIAndroidPanelApp: updateGuardianConfig - 1 - 0.44444448',
        {'entities': [
            (26, 63, 'CONFIG')
        ]}
    ),
    (
        'AnytimeUIAndroidPanelApp: updateGuardianConfig - 2 - 0.21500002',
        {'entities': [
            (26, 63, 'CONFIG')
        ]}
    ),
    (
        'Config changes=1d00 {1.0 ?mcc?mnc [en_US] ldltr sw20dp w39dp h20dp 15000dpi smll land night -touch qwerty/v/v -nav/h winConfig={ mBounds=Rect(0, 0 - 3664, 1920) mAppBounds=Rect(0, 0 - 3664, 1920) mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} s.24}',
        {'entities': [
            (67, 75, 'CONFIG')
        ]}
    ),
    (
        'Override config changes=1d00 {1.0 ?mcc?mnc [en_US] ldltr sw20dp w39dp h20dp 15000dpi smll land night -touch qwerty/v/v -nav/h winConfig={ mBounds=Rect(0, 0 - 3664, 1920) mAppBounds=Rect(0, 0 - 3664, 1920) mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0}',
        {'entities': [
            (76, 84, 'CONFIG')
        ]}
    ),
    (
        "Loading scene 'OverlayScene'",
        {'entities': [
            (15, 27, 'OBJECT_ACTION')
            ]}
    ),
    (
        'DigitalObject instantiated and positioned',
        {'entities': [
            (14, 41, 'OBJECT_ACTION')
            ]}
    ),
    (
        'Unity   : Overlay Awake',
        {'entities': [
            (10, 23, 'OBJECT_ACTION')
            ]}
    ),
    (
        'ShellOverlayApp: ResolveDeviceState: change from Awake to WaitingForSleep', 
        {'entities': [
            (49, 73, 'OBJECT_ACTION')
            ]}
    ),
    (
        'OVRLibrary: query content://com.oculus.ocms.library/apps/com.oculus.ovrmonitormetricsservice', 
        {'entities': [
            (28, 92, 'PACKAGE_NAME')
            ]}
    ),
    (
        'Unity   : OVRManager:Update()',
        {'entities': [
            (10, 29, 'OBJECT_ACTION')
            ]}
    ),
    (
        'VrPlatformOpenXr: xrPollEvent: received XR_TYPE_EVENT_DATA_REFERENCE_SPACE_CHANGE_PENDING event', 
        {'entities': [
            (18, 29, 'API_OPERATION')
            ]}
    ),
    (
        'HapticsUtil: Applying Amplitude Envelope Haptic Effect',
        {'entities': [(22, 54, 'HAPTICS')
            ]}
    ),
    (
        '[OculusApps] [oculus_platform_event] { event_type: oaf_console, message: [curlhttpclient] Executing HTTP request: https://graph.oculus.com/v1.20/105655292295198, source_app_id: 704069629944399,  }', 
        {'entities': [
            (114, 160, 'URL')
            ]}
    ),
    (
        'HapticsUtil: Disabling Haptics: lastPos: 5',
        {'entities': [
            (13, 30, 'HAPTICS')
            ]}
    ),
    (
        'InputDevice_TrackedRemote: OSSDKTRACKING shutting down Haptics',
        {'entities': [
            (41, 62, 'HAPTICS')
            ]}
    ),
    (
        'VrPlatformOpenXr: xrPollEvent: received XR_TYPE_EVENT_DATA_SESSION_STATE_CHANGED: 3 for session 0x2 at time 1305.775385', 
        {'entities': [
            (18, 29, 'API_OPERATION')
            ]}
    ),
    (
        'OpenXR  : ------------ xrCreateSession [start] -----------', 
        {'entities': [
            (23, 46, 'API_OPERATION')
            ]}
    ),
    (
        'OpenXR  : ------------ xrEndSession [start] -----------', 
        {'entities': [
            (23, 43, 'API_OPERATION')
            ]}
    ),
    (
        'OpenXR  : ----------- xrCreateInstance [start] ----------', 
        {'entities': [
            (22, 46, 'API_OPERATION')
            ]}
    ),
    (
        'OpenXR  : ----------- xrDestroyInstance [start] ----------', 
        {'entities': [
            (22, 47, 'API_OPERATION')
            ]}
    ),
    (
        'HapticsUtil: Enabling Haptics',
        {'entities': [
            (13, 29, 'HAPTICS')
            ]}
    ),
        (
        'OVRPlatform: [CurlHttpClient] URI (Sanitized): https://graph.oculus.com//v1.20/push_token_register',
        {'entities': [
            (47, 98, 'URL')
            ]}
    ),
    (
        'ActivityManager: Killing 10143:com.android.packageinstaller/u0a9 (adj 985): empty #17',
        {'entities': [
            (25, 64, 'PROCESS_NAME')
            ]}
    ),
    (
        "Installd: DexInv: --- '/data/app/com.1cZX2HvEXVPkgWXAluK-6Q/abc.apk' ---",
        {'entities': [
            (23, 67, 'PACKAGE_NAME')
            ]}
    ),
    (
        'ActivityTaskManager: START u0 {act=android.intent.action.SEND dat=content://com.igalia.wolvic.provider/external_files/Android/data/com.igalia.wolvic/files/Download/com.apkpure.aegon-1011715.apk flg=0x10810401} from uid 10066',
        {'entities': [
            (62, 193, 'FILEPATH')
            ]}
    ),
    (
        'PackageVerifier: Verifying APK: file:///data/app/ovrmetrics.apk',
        {'entities': [
            (32, 63, 'FILEPATH')
            ]}
    )


]

# Define a function to train the NER model
def train_spacy_ner(training_data, iterations, model=None):
    #if model already exists, import and return it
    if os.path.exists("models/model"):
        nlp = spacy.load("models/model")
        print("Loaded existing model from 'models/model'")
        return nlp
    elif model is not None:
        nlp = spacy.load(model)  # Load existing model
        print("Loaded model '%s'" % model)
    else:
        if not os.path.exists("models"):
            os.makedirs("models")
        nlp = spacy.blank("en")  # Model for part-of-speech tagging
        print("Loaded the 'en' model")

    # Create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    # Add the custom labels to the NER model
    for _, annotations in training_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # Disable the other pipeline components and only train NER
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        # Define the optimizer
        optimizer = nlp.begin_training()

        # Loop for n iterations
        for itn in range(iterations):
            # Shuffle the training data
            examples = training_data
            random.shuffle(examples)

            # Create the batch generator with minibatch()
            batches = minibatch(examples, size=compounding(4.0, 32.0, 1.001))

            # Iterate through minibatches
            losses = {}
            for batch in batches:

                # Convert batch to Example objects
                examples = []
                for text, annots in batch:
                    examples.append(Example.from_dict(nlp.make_doc(text), annots))

                # Update the model
                nlp.update(examples, sgd=optimizer, drop=0.35, losses=losses)

            # Print the iteration loss
            print("Iteration %d: Loss = %.4f" % (itn + 1, losses["ner"]))

    # Save the NLP model to disk
    nlp.to_disk("models/model")
    return nlp

def train_model():
    return train_spacy_ner(TRAIN_DATA, iterations=1000)

def preprocess(text):

        # Regular expression to match URLs
        url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

        # Find all URLs in the string
        urls = re.findall(url_regex, text)

        # Replace periods in non-URL parts of the string
        result = re.sub(url_regex, '###URL###', text)
        result = result.replace('.', ' ')

        # Replace the URLs back into the string
        for url in urls:
            result = result.replace('###URL###', url, 1)

        # Use a regular expression to find all words that are all uppercase
        allcaps_regex = r'\b([A-Z]+)\b'
        allcaps_words = re.findall(allcaps_regex, result)

        # Convert all-caps words to lowercase
        for word in allcaps_words:
            result = result.replace(word, word.lower())

        # Use a regular expression to match all alphabetic characters
        alpha_regex = r'[a-zA-Z]+'

        # Define a lambda function to convert each match to lowercase
        lowercase_fn = lambda match: match.group(0).lower()

        # Use the re.sub() method to replace all matches with their lowercase counterparts
        result = re.sub(alpha_regex, lowercase_fn, result)

        result = result.replace('---', '')

        return result

def find_noun_verbs(sentence):
    # Tokenize the input sentence and get the part-of-speech tag for each token
    tokens = nltk.word_tokenize(sentence)
    pos_tags = nltk.pos_tag(tokens)

    # Find all words in the sentence that are both a noun and a verb
    noun_verbs = []
    for word, pos in pos_tags:
        if pos.startswith('N') and len(wordnet.synsets(word, pos='n')) > 0 and len(wordnet.synsets(word, pos='v')) > 0:
            noun_verbs.append(word)
        elif pos.startswith('V'):
            noun_verbs.append(word)

    return noun_verbs

# load spaCy english nlp for verb phrase parcing
en_nlp = spacy.load("en_core_web_sm")
def find_verb(text):
    doc = en_nlp(text)
    factors = [
        lambda token: token.pos_ == 'VERB',  # POS tag is verb
        lambda token: token.tag_.startswith('VB'),  # Word form or morphological features indicate a verb
    ]

    # Calculate scores for each token
    scores = [sum(factor(token) for factor in factors) for token in doc]
    # Find the token with the highest score
    if max(scores) > 0:
        verb_token = doc[scores.index(max(scores))]
        return verb_token
    else:
        tokens = nltk.word_tokenize(text)
        pos_tags = nltk.pos_tag(tokens)
        for word, pos in pos_tags:
            if pos.startswith('V'):
                for token in doc:
                    if token.text == word:
                        return token

# finds the first verb phrase in the target string
def find_verb_phrase(text):
    verb_token = find_verb(text)
    if verb_token is None:
        return ""
    try:
        verb_phrase = pyinflect.getInflection(WordNetLemmatizer().lemmatize(verb_token.text, "v"), 'VBZ')[0]
    except TypeError:
        return ""
    for child in verb_token.subtree:
        if child.pos_ == 'ADP' or child.pos_ == "PART":
            verb_phrase += " " + child.text
            return verb_phrase
        elif child.pos_ != "VERB" and child.pos_ != "NOUN":
            break
    return verb_phrase


if __name__ == 'main':
    # Test the NER model on the test data
    nlp = train_model()
    for text in TEST_DATA:
        VERB = []

        src = text.split(":")[0]

        text = preprocess(text)
        doc = nlp(text)

        print("Source:" + src)

        print("Entities in '%s'" % text)
        for ent in doc.ents:
            print(ent.label_, ent.text)
        for token in doc:
            if token.pos_ == 'VERB':
                VERB.append(token.text)

        noun_verbs = find_noun_verbs(text)
        if len(noun_verbs)>0:
            for i in range (0,len(noun_verbs)):
                if noun_verbs[i] not in VERB:
                    VERB.append(noun_verbs[i])

        print('VERB: ' + str(VERB)[1:-1])

        print("\n")