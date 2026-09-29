# Hearts — Firebase setup

About ten minutes, once. Until it's done, the hearts work in **local preview**
on `localhost` only (saved in your browser, so you can try the flow), and stay
**hidden** on the live site.

## 1. Create the project

1. Go to <https://console.firebase.google.com> and sign in with your Gmail.
2. **Create a project** → name it anything (e.g. `shiva-meena-story`).
3. Google Analytics: **turn it off** — nothing here needs it.

## 2. Create the database

1. Left menu → **Build → Firestore Database → Create database**.
2. **Location: `asia-south1 (Mumbai)`** — closest to guests in Chennai.
   This one **cannot be changed later**, so pick it deliberately.
3. Choose **Start in production mode** (everything locked) → Create.
4. Open the **Rules** tab, delete what's there, paste the whole of
   `firebase/firestore.rules` from this repo → **Publish**.

## 3. Turn on anonymous sign-in

Guests never see a login. Anonymous sign-in quietly gives each browser an ID,
which is what lets the rules allow exactly one heart per chapter per guest.

1. **Build → Authentication → Get started**.
2. **Sign-in method → Anonymous → Enable → Save**.
3. **Settings → Authorized domains → Add domain** → `siva-sudhan.github.io`
   (`localhost` is already listed).

Skip step 3 and hearts will work on localhost but fail on the live site.

## 4. Connect the page

1. Gear icon → **Project settings → General → Your apps → `</>` (Web)**.
2. Nickname `story page`. Leave **Firebase Hosting unticked**. Register.
3. Copy the `firebaseConfig = { … }` object it shows you.
4. In `index.html`, find

   ```js
   const FIREBASE_CONFIG = null;
   ```

   and replace `null` with the object:

   ```js
   const FIREBASE_CONFIG = {
     apiKey: "AIza…",
     authDomain: "shiva-meena-story.firebaseapp.com",
     projectId: "shiva-meena-story",
     storageBucket: "…",
     messagingSenderId: "…",
     appId: "1:…:web:…"
   };
   ```

These values are **meant to be public** and are safe to commit. They name
the project; they don't unlock it. The rules decide what anyone can do.

## 5. Test before you push

Serve locally and:

1. Leave a heart **with your name** on one chapter.
2. Leave one **anonymously** on another.
3. Click the first again — it should say *"You left a heart here."*
4. In the console, **Firestore → Data**: you should see `chapters` with the
   two documents and `likes` with two entries.

If a heart shows *"That didn't go through"*, open the browser console
(Cmd+Option+J) and send me the line starting `[hearts]`. The rules fail
closed, so a mistake shows up as a refused heart, never as open data.

Your test hearts are real — delete them afterwards (below).

## Removing a heart or a name

The console isn't bound by the rules, so you can edit anything there:

- **Firestore → Data → `chapters` → the chapter** → edit `count`, or open
  `names` and delete an entry (then lower `count` by one to match).
- To let that person heart it again, also delete their entry in `likes`
  (it's named `chapter-id__…`).

## What the rules enforce

- One heart per guest per chapter — checked on the server, not just
  remembered in the browser.
- The count can only rise by exactly one, and only alongside a new heart.
- Names: text only, 1–40 characters, and a guest can only add their own.
- Nobody can edit or delete hearts, and the per-heart ledger isn't readable
  by anyone but its owner.
- Only the eight real chapters can be hearted.

The page reads eight small documents per visit — one per chapter — rather
than every heart ever left, which keeps even a busy day comfortably inside
the free tier.

## Who tapped "Take me there"

When a guest who signed their hearts with a name taps **Take me there**,
the page writes `interest/{their id}` → `{ name, taps, at }`: their name,
how many times they've tapped it, and when they last did. Guests who stayed
anonymous, or never left a heart, aren't recorded.

This needs the current `firestore.rules` — re-paste and **Publish** it after
updating. Only you can read `interest` (in the console); guests can only add
to their own entry.
