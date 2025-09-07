#!/bin/bash

# VNC password
VNC_PASSWORD=${PASSWORD:-ubuntu}
USER=${USER:-ubuntu}
PASSWORD=${PASSWORD:-ubuntu}
HOME=/home/$USER

echo "$USER:$PASSWORD" | /usr/sbin/chpasswd 2> /dev/null || echo ""
cp -r /root/{.config,.gtkrc-2.0,.asoundrc} ${HOME} 2>/dev/null
chown -R $USER:$USER ${HOME}
[ -d "/dev/snd" ] && chgrp -R adm /dev/snd

mkdir -p $HOME/.vnc
echo "$VNC_PASSWORD" | vncpasswd -f > $HOME/.vnc/passwd
chmod 600 $HOME/.vnc/passwd
chown -R $USER:$USER $HOME
sed -i "s/password = WebUtil.getConfigVar('password');/password = '$VNC_PASSWORD'/" /usr/lib/novnc/app/ui.js

# xstartup
XSTARTUP_PATH=$HOME/.vnc/xstartup
cat << EOF > $XSTARTUP_PATH
#!/bin/sh
unset DBUS_SESSION_BUS_ADDRESS
mate-session
EOF
chown $USER:$USER $XSTARTUP_PATH
chmod 755 $XSTARTUP_PATH

# vncserver launch
VNCRUN_PATH=$HOME/.vnc/vnc_run.sh
cat << EOF > $VNCRUN_PATH
#!/bin/sh

# Workaround for issue when image is created with "docker commit".
# Thanks to @SaadRana17
# https://github.com/Tiryoh/docker-ros2-desktop-vnc/issues/131#issuecomment-2184156856

if [ -e /tmp/.X1-lock ]; then
    rm -f /tmp/.X1-lock
fi
if [ -e /tmp/.X11-unix/X1 ]; then
    rm -f /tmp/.X11-unix/X1
fi

if [ $(uname -m) = "aarch64" ]; then
    LD_PRELOAD=/lib/aarch64-linux-gnu/libgcc_s.so.1 vncserver :1 -fg -geometry 1920x1080 -depth 24
else
    vncserver :1 -fg -geometry 1920x1080 -depth 24
fi
EOF

# Supervisor
CONF_PATH=/etc/supervisor/conf.d/supervisord.conf
cat << EOF > $CONF_PATH
[supervisord]
nodaemon=true
user=root
[program:vnc]
command=gosu '$USER' bash '$VNCRUN_PATH'
[program:novnc]
command=gosu '$USER' bash -c "websockify --web=/usr/lib/novnc 80 localhost:5901"
EOF

# colcon
BASHRC_PATH=$HOME/.bashrc
grep -F "source /opt/ros/$ROS_DISTRO/setup.bash" $BASHRC_PATH || echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> $BASHRC_PATH
grep -F "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" $BASHRC_PATH || echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> $BASHRC_PATH
chown $USER:$USER $BASHRC_PATH

# Fix rosdep permission
mkdir -p $HOME/.ros
cp -r /root/.ros/rosdep $HOME/.ros/rosdep
chown -R $USER:$USER $HOME/.ros

# Add terminator shortcut
mkdir -p $HOME/Desktop
cat << EOF > $HOME/Desktop/terminator.desktop
[Desktop Entry]
Name=Terminator
Comment=Multiple terminals in one window
TryExec=terminator
Exec=terminator
Icon=terminator
Type=Application
Categories=GNOME;GTK;Utility;TerminalEmulator;System;
StartupNotify=true
X-Ubuntu-Gettext-Domain=terminator
X-Ayatana-Desktop-Shortcuts=NewWindow;
Keywords=terminal;shell;prompt;command;commandline;
[NewWindow Shortcut Group]
Name=Open a New Window
Exec=terminator
TargetEnvironment=Unity
EOF
cat << EOF > $HOME/Desktop/firefox.desktop
[Desktop Entry]
Version=1.0
Name=Firefox Web Browser
Name[ar]=ŸÖÿ™ÿµŸÅÿ≠ ÿßŸÑŸàŸäÿ® ŸÅŸéŸäŸéÿ±ŸÅŸèŸÉŸíÿ≥
Name[ast]=Restolador web Firefox
Name[bn]=‡¶´‡¶æ‡¶Ø‡¶º‡¶æ‡¶∞‡¶´‡¶ï‡ßç‡¶∏ ‡¶ì‡¶Ø‡¶º‡ßá‡¶¨ ‡¶¨‡ßç‡¶∞‡¶æ‡¶â‡¶ú‡¶æ‡¶∞
Name[ca]=Navegador web Firefox
Name[cs]=Firefox Webov√Ω prohl√≠≈æeƒç
Name[da]=Firefox - internetbrowser
Name[el]=Œ†ŒµœÅŒπŒ∑Œ≥Œ∑œÑŒÆœÇ Firefox
Name[es]=Navegador web Firefox
Name[et]=Firefoxi veebibrauser
Name[fa]=ŸÖÿ±Ÿàÿ±⁄Øÿ± ÿß€åŸÜÿ™ÿ±ŸÜÿ™€å Firefox
Name[fi]=Firefox-selain
Name[fr]=Navigateur Web Firefox
Name[gl]=Navegador web Firefox
Name[he]=◊ì◊§◊ì◊§◊ü ◊î◊ê◊ô◊†◊ò◊®◊†◊ò Firefox
Name[hr]=Firefox web preglednik
Name[hu]=Firefox webb√∂ng√©sz≈ë
Name[it]=Firefox Browser Web
Name[ja]=Firefox „Ç¶„Çß„Éñ„Éª„Éñ„É©„Ç¶„Ç∂
Name[ko]=Firefox Ïõπ Î∏åÎùºÏö∞Ï†Ä
Name[ku]=Geroka tor√™ Firefox
Name[lt]=Firefox interneto nar≈°yklƒó
Name[nb]=Firefox Nettleser
Name[nl]=Firefox webbrowser
Name[nn]=Firefox Nettlesar
Name[no]=Firefox Nettleser
Name[pl]=PrzeglƒÖdarka WWW Firefox
Name[pt]=Firefox Navegador Web
Name[pt_BR]=Navegador Web Firefox
Name[ro]=Firefox ‚Äì Navigator Internet
Name[ru]=–í–µ–±-–±—Ä–∞—É–∑–µ—Ä Firefox
Name[sk]=Firefox - internetov√Ω prehliadaƒç
Name[sl]=Firefox spletni brskalnik
Name[sv]=Firefox webbl√§sare
Name[tr]=Firefox Web Tarayƒ±cƒ±sƒ±
Name[ug]=Firefox ÿ™Ÿàÿ±ŸÉ€Üÿ±⁄Ø€à
Name[uk]=–í–µ–±-–±—Ä–∞—É–∑–µ—Ä Firefox
Name[vi]=Tr√¨nh duy·ªát web Firefox
Name[zh_CN]=Firefox ÁΩëÁªúÊµèËßàÂô®
Name[zh_TW]=Firefox Á∂≤Ë∑ØÁÄèË¶ΩÂô®
Comment=Browse the World Wide Web
Comment[ar]=ÿ™ÿµŸÅÿ≠ ÿßŸÑÿ¥ÿ®ŸÉÿ© ÿßŸÑÿπŸÜŸÉÿ®Ÿàÿ™Ÿäÿ© ÿßŸÑÿπÿßŸÑŸÖŸäÿ©
Comment[ast]=Restola pela Rede
Comment[bn]=‡¶á‡¶®‡ßç‡¶ü‡¶æ‡¶∞‡¶®‡ßá‡¶ü ‡¶¨‡ßç‡¶∞‡¶æ‡¶â‡¶ú ‡¶ï‡¶∞‡ßÅ‡¶®
Comment[ca]=Navegueu per la web
Comment[cs]=Prohl√≠≈æen√≠ str√°nek World Wide Webu
Comment[da]=Surf p√• internettet
Comment[de]=Im Internet surfen
Comment[el]=ŒúœÄŒøœÅŒµŒØœÑŒµ ŒΩŒ± œÄŒµœÅŒπŒ∑Œ≥Œ∑Œ∏ŒµŒØœÑŒµ œÉœÑŒø Œ¥ŒπŒ±Œ¥ŒØŒ∫œÑœÖŒø (Web)
Comment[es]=Navegue por la web
Comment[et]=Lehitse veebi
Comment[fa]=ÿµŸÅÿ≠ÿßÿ™ ÿ¥ÿ®⁄©Ÿá ÿ¨ŸáÿßŸÜ€å ÿß€åŸÜÿ™ÿ±ŸÜÿ™ ÿ±ÿß ŸÖÿ±Ÿàÿ± ŸÜŸÖÿß€å€åÿØ
Comment[fi]=Selaa Internetin WWW-sivuja
Comment[fr]=Naviguer sur le Web
Comment[gl]=Navegar pola rede
Comment[he]=◊í◊ú◊ô◊©◊î ◊ë◊®◊ó◊ë◊ô ◊î◊ê◊ô◊†◊ò◊®◊†◊ò
Comment[hr]=Pretra≈æite web
Comment[hu]=A vil√°gh√°l√≥ b√∂ng√©sz√©se
Comment[it]=Esplora il web
Comment[ja]=„Ç¶„Çß„Éñ„ÇíÈñ≤Ë¶ß„Åó„Åæ„Åô
Comment[ko]=ÏõπÏùÑ ÎèåÏïÑ Îã§ÎãôÎãàÎã§
Comment[ku]=Li tor√™ bigere
Comment[lt]=Nar≈°ykite internete
Comment[nb]=Surf p√• nettet
Comment[nl]=Verken het internet
Comment[nn]=Surf p√• nettet
Comment[no]=Surf p√• nettet
Comment[pl]=PrzeglƒÖdanie stron WWW
Comment[pt]=Navegue na Internet
Comment[pt_BR]=Navegue na Internet
Comment[ro]=Naviga»õi pe Internet
Comment[ru]=–î–æ—Å—Ç—É–ø –≤ –ò–Ω—Ç–µ—Ä–Ω–µ—Ç
Comment[sk]=Prehliadanie internetu
Comment[sl]=Brskajte po spletu
Comment[sv]=Surfa p√• webben
Comment[tr]=ƒ∞nternet'te Gezinin
Comment[ug]=ÿØ€áŸÜŸäÿßÿØŸâŸÉŸâ ÿ™Ÿàÿ±ÿ®€ïÿ™ŸÑ€ïÿ±ŸÜŸâ ŸÉ€Üÿ±⁄ØŸâŸÑŸâ ÿ®ŸàŸÑŸâÿØ€á
Comment[uk]=–ü–µ—Ä–µ–≥–ª—è–¥ —Å—Ç–æ—Ä—ñ–Ω–æ–∫ –Ü–Ω—Ç–µ—Ä–Ω–µ—Ç—É
Comment[vi]=ƒê·ªÉ duy·ªát c√°c trang web
Comment[zh_CN]=ÊµèËßà‰∫íËÅîÁΩë
Comment[zh_TW]=ÁÄèË¶ΩÁ∂≤ÈöõÁ∂≤Ë∑Ø
GenericName=Web Browser
GenericName[ar]=ŸÖÿ™ÿµŸÅÿ≠ ŸàŸäÿ®
GenericName[ast]=Restolador Web
GenericName[bn]=‡¶ì‡¶Ø‡¶º‡ßá‡¶¨ ‡¶¨‡ßç‡¶∞‡¶æ‡¶â‡¶ú‡¶æ‡¶∞
GenericName[ca]=Navegador web
GenericName[cs]=Webov√Ω prohl√≠≈æeƒç
GenericName[da]=Webbrowser
GenericName[el]=Œ†ŒµœÅŒπŒ∑Œ≥Œ∑œÑŒÆœÇ Œ¥ŒπŒ±Œ¥ŒπŒ∫œÑœçŒøœÖ
GenericName[es]=Navegador web
GenericName[et]=Veebibrauser
GenericName[fa]=ŸÖÿ±Ÿàÿ±⁄Øÿ± ÿß€åŸÜÿ™ÿ±ŸÜÿ™€å
GenericName[fi]=WWW-selain
GenericName[fr]=Navigateur Web
GenericName[gl]=Navegador Web
GenericName[he]=◊ì◊§◊ì◊§◊ü ◊ê◊ô◊†◊ò◊®◊†◊ò
GenericName[hr]=Web preglednik
GenericName[hu]=Webb√∂ng√©sz≈ë
GenericName[it]=Browser web
GenericName[ja]=„Ç¶„Çß„Éñ„Éª„Éñ„É©„Ç¶„Ç∂
GenericName[ko]=Ïõπ Î∏åÎùºÏö∞Ï†Ä
GenericName[ku]=Geroka tor√™
GenericName[lt]=Interneto nar≈°yklƒó
GenericName[nb]=Nettleser
GenericName[nl]=Webbrowser
GenericName[nn]=Nettlesar
GenericName[no]=Nettleser
GenericName[pl]=PrzeglƒÖdarka WWW
GenericName[pt]=Navegador Web
GenericName[pt_BR]=Navegador Web
GenericName[ro]=Navigator Internet
GenericName[ru]=–í–µ–±-–±—Ä–∞—É–∑–µ—Ä
GenericName[sk]=Internetov√Ω prehliadaƒç
GenericName[sl]=Spletni brskalnik
GenericName[sv]=Webbl√§sare
GenericName[tr]=Web Tarayƒ±cƒ±
GenericName[ug]=ÿ™Ÿàÿ±ŸÉ€Üÿ±⁄Ø€à
GenericName[uk]=–í–µ–±-–±—Ä–∞—É–∑–µ—Ä
GenericName[vi]=Tr√¨nh duy·ªát Web
GenericName[zh_CN]=ÁΩëÁªúÊµèËßàÂô®
GenericName[zh_TW]=Á∂≤Ë∑ØÁÄèË¶ΩÂô®
Keywords=Internet;WWW;Browser;Web;Explorer
Keywords[ar]=ÿßŸÜÿ™ÿ±ŸÜÿ™;ÿ•ŸÜÿ™ÿ±ŸÜÿ™;ŸÖÿ™ÿµŸÅÿ≠;ŸàŸäÿ®;Ÿàÿ®
Keywords[ast]=Internet;WWW;Restolador;Web;Esplorador
Keywords[ca]=Internet;WWW;Navegador;Web;Explorador;Explorer
Keywords[cs]=Internet;WWW;Prohl√≠≈æeƒç;Web;Explorer
Keywords[da]=Internet;Internettet;WWW;Browser;Browse;Web;Surf;Nettet
Keywords[de]=Internet;WWW;Browser;Web;Explorer;Webseite;Site;surfen;online;browsen
Keywords[el]=Internet;WWW;Browser;Web;Explorer;ŒîŒπŒ±Œ¥ŒØŒ∫œÑœÖŒø;Œ†ŒµœÅŒπŒ∑Œ≥Œ∑œÑŒÆœÇ;Firefox;Œ¶ŒπœÅŒµœÜŒøœá;ŒôŒΩœÑŒµœÅŒΩŒµœÑ
Keywords[es]=Explorador;Internet;WWW
Keywords[fi]=Internet;WWW;Browser;Web;Explorer;selain;Internet-selain;internetselain;verkkoselain;netti;surffaa
Keywords[fr]=Internet;WWW;Browser;Web;Explorer;Fureteur;Surfer;Navigateur
Keywords[he]=◊ì◊§◊ì◊§◊ü;◊ê◊ô◊†◊ò◊®◊†◊ò;◊®◊©◊™;◊ê◊™◊®◊ô◊ù;◊ê◊™◊®;◊§◊ô◊ô◊®◊§◊ï◊ß◊°;◊û◊ï◊ñ◊ô◊ú◊î;
Keywords[hr]=Internet;WWW;preglednik;Web
Keywords[hu]=Internet;WWW;B√∂ng√©sz≈ë;Web;H√°l√≥;Net;Explorer
Keywords[it]=Internet;WWW;Browser;Web;Navigatore
Keywords[is]=Internet;WWW;Vafri;Vefur;Netvafri;Flakk
Keywords[ja]=Internet;WWW;Web;„Ç§„É≥„Çø„Éº„Éç„ÉÉ„Éà;„Éñ„É©„Ç¶„Ç∂;„Ç¶„Çß„Éñ;„Ç®„ÇØ„Çπ„Éó„É≠„Éº„É©
Keywords[nb]=Internett;WWW;Nettleser;Explorer;Web;Browser;Nettside
Keywords[nl]=Internet;WWW;Browser;Web;Explorer;Verkenner;Website;Surfen;Online
Keywords[pt]=Internet;WWW;Browser;Web;Explorador;Navegador
Keywords[pt_BR]=Internet;WWW;Browser;Web;Explorador;Navegador
Keywords[ru]=Internet;WWW;Browser;Web;Explorer;–∏–Ω—Ç–µ—Ä–Ω–µ—Ç;–±—Ä–∞—É–∑–µ—Ä;–≤–µ–±;—Ñ–∞–π—Ä—Ñ–æ–∫—Å;–æ–≥–Ω–µ–ª–∏—Å
Keywords[sk]=Internet;WWW;Prehliadaƒç;Web;Explorer
Keywords[sl]=Internet;WWW;Browser;Web;Explorer;Brskalnik;Splet
Keywords[tr]=ƒ∞nternet;WWW;Tarayƒ±cƒ±;Web;Gezgin;Web sitesi;Site;s√∂rf;√ßevrimi√ßi;tara
Keywords[uk]=Internet;WWW;Browser;Web;Explorer;–Ü–Ω—Ç–µ—Ä–Ω–µ—Ç;–º–µ—Ä–µ–∂–∞;–ø–µ—Ä–µ–≥–ª—è–¥–∞—á;–æ–≥–ª—è–¥–∞—á;–±—Ä–∞—É–∑–µ—Ä;–≤–µ–±;—Ñ–∞–π—Ä—Ñ–æ–∫—Å;–≤–æ–≥–Ω–µ–ª–∏—Å;–ø–µ—Ä–µ–≥–ª—è–¥
Keywords[vi]=Internet;WWW;Browser;Web;Explorer;Tr√¨nh duy·ªát;Trang web
Keywords[zh_CN]=Internet;WWW;Browser;Web;Explorer;ÁΩëÈ°µ;ÊµèËßà;‰∏äÁΩë;ÁÅ´Áãê;Firefox;ff;‰∫íËÅîÁΩë;ÁΩëÁ´ô;
Keywords[zh_TW]=Internet;WWW;Browser;Web;Explorer;Á∂≤ÈöõÁ∂≤Ë∑Ø;Á∂≤Ë∑Ø;ÁÄèË¶ΩÂô®;‰∏äÁ∂≤;Á∂≤È†Å;ÁÅ´Áãê
Exec=firefox %u
Terminal=false
X-MultipleArgs=false
Type=Application
Icon=firefox
Categories=GNOME;GTK;Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;application/xml;application/rss+xml;application/rdf+xml;image/gif;image/jpeg;image/png;x-scheme-handler/http;x-scheme-handler/https;x-scheme-handler/ftp;x-scheme-handler/chrome;video/webm;application/x-xpinstall;
StartupNotify=true
Actions=new-window;new-private-window;

[Desktop Action new-window]
Name=Open a New Window
Name[ar]=ÿßŸÅÿ™ÿ≠ ŸÜÿßŸÅÿ∞ÿ© ÿ¨ÿØŸäÿØÿ©
Name[ast]=Abrir una ventana nueva
Name[bn]=Abrir una ventana nueva
Name[ca]=Obre una finestra nova
Name[cs]=Otev≈ô√≠t nov√© okno
Name[da]=√Öbn et nyt vindue
Name[de]=Ein neues Fenster √∂ffnen
Name[el]=ŒùŒ≠Œø œÄŒ±œÅŒ¨Œ∏œÖœÅŒø
Name[es]=Abrir una ventana nueva
Name[fi]=Avaa uusi ikkuna
Name[fr]=Ouvrir une nouvelle fen√™tre
Name[gl]=Abrir unha nova xanela
Name[he]=◊§◊™◊ô◊ó◊™ ◊ó◊ú◊ï◊ü ◊ó◊ì◊©
Name[hr]=Otvori novi prozor
Name[hu]=√öj ablak nyit√°sa
Name[it]=Apri una nuova finestra
Name[ja]=Êñ∞„Åó„ÅÑ„Ç¶„Ç£„É≥„Éâ„Ç¶„ÇíÈñã„Åè
Name[ko]=ÏÉà Ï∞Ω Ïó¥Í∏∞
Name[ku]=Paceyeke n√ª veke
Name[lt]=Atverti naujƒÖ langƒÖ
Name[nb]=√Öpne et nytt vindu
Name[nl]=Nieuw venster openen
Name[pt]=Abrir nova janela
Name[pt_BR]=Abrir nova janela
Name[ro]=Deschide o fereastrƒÉ nouƒÉ
Name[ru]=–ù–æ–≤–æ–µ –æ–∫–Ω–æ
Name[sk]=Otvori≈• nov√© okno
Name[sl]=Odpri novo okno
Name[sv]=√ñppna ett nytt f√∂nster
Name[tr]=Yeni pencere a√ß
Name[ug]=Ÿä€ê⁄≠Ÿâ ŸÉ€Üÿ≤ŸÜ€ïŸÉ ÿ¶€ê⁄ÜŸâÿ¥
Name[uk]=–í—ñ–¥–∫—Ä–∏—Ç–∏ –Ω–æ–≤–µ –≤—ñ–∫–Ω–æ
Name[vi]=M·ªü c·ª≠a s·ªï m·ªõi
Name[zh_CN]=Êñ∞Âª∫Á™óÂè£
Name[zh_TW]=ÈñãÂïüÊñ∞Ë¶ñÁ™ó
Exec=firefox -new-window

[Desktop Action new-private-window]
Name=Open a New Private Window
Name[ar]=ÿßŸÅÿ™ÿ≠ ŸÜÿßŸÅÿ∞ÿ© ÿ¨ÿØŸäÿØÿ© ŸÑŸÑÿ™ÿµŸÅÿ≠ ÿßŸÑÿÆÿßÿµ
Name[ca]=Obre una finestra nova en mode d'inc√≤gnit
Name[cs]=Otev≈ô√≠t nov√© anonymn√≠ okno
Name[de]=Ein neues privates Fenster √∂ffnen
Name[el]=ŒùŒ≠Œø ŒπŒ¥ŒπœâœÑŒπŒ∫œå œÄŒ±œÅŒ¨Œ∏œÖœÅŒø
Name[es]=Abrir una ventana privada nueva
Name[fi]=Avaa uusi yksityinen ikkuna
Name[fr]=Ouvrir une nouvelle fen√™tre de navigation priv√©e
Name[he]=◊§◊™◊ô◊ó◊™ ◊ó◊ú◊ï◊ü ◊í◊ú◊ô◊©◊î ◊§◊®◊ò◊ô◊™ ◊ó◊ì◊©
Name[hu]=√öj priv√°t ablak nyit√°sa
Name[it]=Apri una nuova finestra anonima
Name[nb]=√Öpne et nytt privat vindu
Name[ru]=–ù–æ–≤–æ–µ –ø—Ä–∏–≤–∞—Ç–Ω–æ–µ –æ–∫–Ω–æ
Name[sl]=Odpri novo okno zasebnega brskanja
Name[sv]=√ñppna ett nytt privat f√∂nster
Name[tr]=Yeni gizli pencere a√ß
Name[uk]=–í—ñ–¥–∫—Ä–∏—Ç–∏ –Ω–æ–≤–µ –≤—ñ–∫–Ω–æ —É –ø–æ—Ç–∞–π–ª–∏–≤–æ–º—É —Ä–µ–∂–∏–º—ñ
Name[zh_TW]=ÈñãÂïüÊñ∞Èö±ÁßÅÁÄèË¶ΩË¶ñÁ™ó
Exec=firefox -private-window
EOF
cat << EOF > $HOME/Desktop/codium.desktop
[Desktop Entry]
Name=VSCodium
Comment=Code Editing. Redefined.
GenericName=Text Editor
Exec=/usr/share/codium/codium --unity-launch %F
Icon=vscodium
Type=Application
StartupNotify=false
StartupWMClass=VSCodium
Categories=TextEditor;Development;IDE;
MimeType=text/plain;inode/directory;application/x-codium-workspace;
Actions=new-empty-window;
Keywords=vscode;

[Desktop Action new-empty-window]
Name=New Empty Window
Exec=/usr/share/codium/codium --new-window %F
Icon=vscodium
EOF
chown -R $USER:$USER $HOME/Desktop

# clearup
PASSWORD=
VNC_PASSWORD=

echo "============================================================================================"
echo "NOTE 1: --security-opt seccomp=unconfined flag is required to launch Ubuntu Jammy based image."
echo -e "See \e]8;;https://github.com/Tiryoh/docker-ros2-desktop-vnc/pull/56\e\\https://github.com/Tiryoh/docker-ros2-desktop-vnc/pull/56\e]8;;\e\\"
echo "============================================================================================"

exec /bin/tini -- supervisord -n -c /etc/supervisor/supervisord.conf
