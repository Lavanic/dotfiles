// Applied over prefs.js at every startup. install.sh links this into the
// default profile, since the profile dir name is random per machine.

user_pref("sidebar.revamp", true);
user_pref("sidebar.verticalTabs", true);
user_pref("sidebar.visibility", "expand-on-hover");

user_pref("browser.ctrlTab.sortByRecentlyUsed", true);
user_pref("browser.tabs.insertAfterCurrent", true);
user_pref("browser.tabs.closeWindowWithLastTab", false);

user_pref("browser.compactmode.show", true);
user_pref("browser.uidensity", 1);
user_pref("browser.urlbar.trimURLs", false);

// KDE file dialog instead of GTK
user_pref("widget.use-xdg-desktop-portal.file-picker", 1);

user_pref("browser.newtabpage.activity-stream.showSponsored", false);
user_pref("browser.newtabpage.activity-stream.showSponsoredTopSites", false);
user_pref("browser.aboutConfig.showWarning", false);
