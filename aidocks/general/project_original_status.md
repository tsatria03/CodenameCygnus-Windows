---
name: project_original_status
description: "Where the original Codename Cygnus stands, researched 2026-10-18: Reactive Studios became Earplay; the iOS app is gone from the App Store; Earplay relaunched the story free on Alexa and Google Assistant; the port plays version 1.3.2, recovered with theblindgamer50's help."
metadata:
  node_type: memory
  type: reference
---

Researched on 2026-10-18, when the dev asked to confirm the original is no longer available and to update the credits ([[project_solo]]).

**Confirmed:**
- **The iOS app is gone from the App Store.** Apple's own lookup for its bundle ID, `net.reactivestudios.codenamecygnus` (`itunes.apple.com/lookup?bundleId=...`), returns no result in the US, the UK, Canada or Australia, and an App Store search for "codename cygnus" finds no such app.
- **Reactive Studios became Earplay.** Earplay's site calls itself founded "in 2013 with the release of Codename Cygnus, the first ever voice operated interactive audio drama on iOS" (earplay.com/about), and its relaunch post says the company re-branded as Earplay.
- **The story was relaunched free, but not as the app.** Earplay's page for it says it "is reactivated on Amazon Alexa and Google Assistant, with updated audio and voice prompts", "Available On: Amazon Alexa, Google Assistant", FREE, with "all 7 chapters" (earplay.com/stories/codename-cygnus). It lists no iOS app.
- **Episodes were once bought in the app:** Mission 1 for $2.99, or each episode for $0.99, after a price cut in the 1.x update that added Game Center achievements and VoiceOver; the Prologue was free (Cult of Mac, 2014-01-16).

**Version 1.4.0, from the app itself** (the dev's own copy, `Codename Cygnus 1.4.0.ipa`, looked at on 2026-10-18 without unpacking it, and without reading the buyer's account details in its `iTunesMetadata.plist`):
- **Earplay's rewrite under the same App Store entry:** the bundle ID is still `net.reactivestudios.codenamecygnus` and the name "Codename Cygnus", but the seller is "Earplay, Inc." and the app inside is `earplay-ios-v2`, written in Swift (Alamofire, Moya, RxSwift, Bose's wearable-audio kit for head tracking), for iOS 11.4 and later. 1.3.2's `Cygnus` was Objective-C. It still listens with OpenEars and the same PocketSphinx English model.
- **No story and no recordings:** 26 MB, with no story data, voices, ambiences or previews; it streams them from Earplay's servers, behind an account (its screens have Log Out, Change Password, Change Email and Change Username). Its one story screen says "Codename Cygnus" and "double tap to play".
- **No shop:** none of its screens has a word about buying, prices, restoring purchases or unlocking (the only such words in it are the speech model's dictionary). This bears out the dev: the newest version no longer sells missions, as Earplay made every chapter free.
- **Not readable:** the main binary is still FairPlay-encrypted (`cryptid` 1), so its code, any leftover purchase code and its server's address cannot be read. Apple's `hasOrEverHasHadIAP` is true, but "ever" covers 1.x's sold episodes.
- **So 1.3.2 is the version to port,** as the port does: 1.4.0 holds no story and depends on servers that may no longer run.

**Not confirmed:**
- That 1.4.0's encrypted code sells nothing; its screens show no shop, but the code itself cannot be read.
- Whether the Alexa or Google Assistant versions still run today. Earplay's pages still list them, and no source found says they were withdrawn. (Google ended Conversational Actions for Assistant in June 2023, so the Google version is very likely gone, but no source about Codename Cygnus itself says so.)

So the credits say only what is confirmed: Reactive Studios is now Earplay, and the original iPhone and iPad app is no longer on the App Store.

**Sources:**
- https://earplay.com/stories/codename-cygnus/
- https://earplay.com/about/
- https://www.earplay.com/codename-cygnus-has-returned/ (moved to Medium, which would not open; read through search results)
- https://www.cultofmac.com/news/fantastic-spy-game-codename-cygnus-gets-better-cheaper
- https://itunes.apple.com/lookup?bundleId=net.reactivestudios.codenamecygnus
