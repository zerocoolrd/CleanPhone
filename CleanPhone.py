# -*- coding: utf-8 -*-
import os
import subprocess
import threading
import json
import urllib.request
import sys
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

CURRENT_VERSION = "2.1.2 Pro" # FIX: Módulo "Sálvame mi app" con mensaje personalizado, nombres limpios y botón centrado.
VERSION_URL = "https://raw.githubusercontent.com/zerocoolrd/CleanPhone/main/version.json"

# ==========================================
# 1. LISTAS DE BLOATWARE Y DATOS (CARRIER / SYSTEM)
# ==========================================
CARRIER_BLOATWARE = {
    "Altice / Tricom (LATAM / Caribe)": [
        ("Mi Altice", "com.altice.mialtice"),
        ("Altice Play (Tricom)", "com.hottricom.tricom.tricom"),
        ("Altice Play", "com.altice.alticeplay"),
        ("Altice Music (Kuack)", "com.kuackmedia.orange"),
        ("Altice WiFi", "com.altice.wifi"),
    ],
    "Claro (LATAM)": [
        ("Mi Claro", "com.claro.eam.latin.mivariable"),
        ("Claro Musica", "com.claro.claromusica.latam"),
        ("Claro Video", "com.claro.clarovideo"),
        ("Claro Juegos", "com.claro.juegos"),
        ("Contenedor Claro", "com.claro.container"),
    ],
    "AT&T (EE. UU. / MX)": [
        ("AT&T MyWireless", "com.att.myWireless"),
        ("AT&T Call Protect", "com.att.callprotect"),
        ("AT&T Personal Cloud", "com.att.personalcloud"),
        ("AT&T Smart Wi-Fi", "com.att.android.attsmartwifi"),
        ("AT&T Mobile Key", "com.att.csoiam.mobilekey"),
        ("AT&T IQI / Analytics", "com.att.iqi"),
        ("AppFlash / DTI", "com.dti.att"),
        ("Digital Turbine News", "com.digitalturbine.android.apps.news.att"),
    ],
    "T-Mobile / Sprint (EE. UU.)": [
        ("T-Mobile Name ID", "com.tmobile.services.nameid"),
        ("T-Mobile Tuesdays", "com.tmobile.pr.tuesdays"),
        ("T-Mobile Visual Voicemail", "com.tmobile.vvm.application"),
        ("T-Mobile App Experience", "com.tmobile.pr.mytmobile"),
        ("Sprint Zone", "com.sprint.zone"),
        ("Sprint Hub", "com.sprint.ce.spdmode"),
    ],
    "Verizon / Xfinity Mobile (EE. UU.)": [
        ("My Verizon", "com.vzw.hss.myverizon"),
        ("Verizon Cloud", "com.vzw.hss.myverizon"),
        ("Verizon Message+", "com.verizon.messaging.vzmsgs"),
        ("Verizon Location Agent", "com.vzw.hs.android.modemservice"),
        ("Verizon Security", "com.asurion.android.verizon.vsecurity"),
        ("Verizon Login Engine", "com.verizon.loginengine.unbranded"),
        ("Xfinity Mobile App", "com.xfinitymobile.myaccount"),
        ("Xfinity App", "com.xfinity.digitalhome"),
        ("Pocket Geek Tech Repair", "com.pocketgeek.android"),
    ],
    "Orange (LATAM / Europa)": [
        ("My Orange / eCare", "com.orange.mobile.ecare"),
        ("Orange Music / Kuack", "com.kuackmedia.orange"),
        ("My Orange Global", "com.orange.myorange"),
        ("Orange TV", "com.orange.ovetv"),
        ("Orange Money", "com.orange.orangemoney"),
    ],
    "Movistar / Telefonica (HISPAM)": [
        ("Mi Movistar", "com.telefonica.miservicios"),
        ("Movistar Play", "com.movistar.play"),
        ("Movistar Cloud", "com.movistar.cloud"),
    ],
    "TIM (Brasil)": [
        ("Meu TIM", "br.com.tim.webtim"),
        ("TIM Music", "br.com.tim.timmusicbydeezer"),
    ],
    "Telcel (México)": [
        ("Mi Telcel", "com.itelcel.socio.app.telcel"),
        ("Telcel Pay", "com.telcel.pay"),
    ]
}

SYSTEM_BLOATWARE = {
    "Google Services & Apps": [
        ("Google Buscador / App", "com.google.android.googlequicksearchbox"),
        ("Google Drive", "com.google.android.apps.docs"),
        ("Google Maps", "com.google.android.apps.maps"),
        ("Google TV / Play Movies", "com.google.android.videos"),
        ("Google Meet / Duo", "com.google.android.apps.tachyon"),
        ("Google Fotos", "com.google.android.apps.photos"),
        ("YouTube Music", "com.google.android.apps.youtube.music"),
        ("Google Home (Chromecast)", "com.google.android.apps.chromecast.app"),
        ("Google Keep (Notas)", "com.google.android.keep"),
        ("Google Assistant (Asistente)", "com.google.android.apps.googleassistant"),
        ("Google Wallet (Billetera)", "com.google.android.apps.walletnfcrel"),
        ("Centro de Seguridad Google", "com.google.android.safetycenter.resources"),
    ],
    "Samsung Apps & Ecosistema": [
        ("Samsung Members", "com.samsung.oh"),
        ("Samsung Members (VOC)", "com.samsung.android.voc"),
        ("Galaxy Wearable Manager", "com.samsung.android.app.watchmanager"),
        ("Galaxy Wearable Stub", "com.samsung.android.app.watchmanagerstub"),
        ("Samsung Radio FM", "com.sec.android.app.fm"),
        ("Grabadora de Voz", "com.sec.android.app.voicenote"),
        ("Samsung Global Goals", "com.samsung.sree"),
        ("Microsoft OneDrive", "com.microsoft.skydrive"),
        ("Microsoft Outlook", "com.microsoft.office.outlook"),
        ("Microsoft Office Hub", "com.microsoft.office.officehubrow"),
        ("Samsung SmartThings", "com.samsung.android.oneconnect"),
        ("Samsung Smart Switch", "com.sec.android.easyMover"),
        ("Samsung Notes", "com.samsung.android.app.notes"),
        ("Samsung Health", "com.sec.android.app.shealth"),
        ("Visual Voicemail (Samsung)", "com.samsung.vvm"),
        ("Navegador Samsung", "com.sec.android.app.sbrowser"),
        ("Galaxy Store", "com.sec.android.app.samsungapps"),
        ("Samsung Free / News", "com.samsung.android.app.spage"),
        ("Bixby Agent", "com.samsung.android.bixby.agent"),
        ("Bixby Service", "com.samsung.android.bixby.wakeup"),
        ("Samsung Pass", "com.samsung.android.samsungpass"),
        ("Tienda de Temas", "com.samsung.android.themestore"),
        ("Samsung Kids", "com.sec.android.app.kidshome"),
        ("Game Launcher / Hub", "com.samsung.android.game.gamehome"),
        ("Google Play Services for AR", "com.google.ar.core"),
        ("Game Tools", "com.samsung.android.game.gametools"),
        ("Samsung DiagMon Agent", "com.sec.android.diagmonagent"),
        ("Samsung Rubin Service", "com.samsung.android.rubin.app"),
        ("Samsung Analytics Uploader", "com.samsung.android.knox.analytics.uploader"),
    ],
    "Juegos y Entretenimiento (Bloatware)": [
        ("Bubble Shooter Puzzle Game", "bubble.shooter.pop.marble.cannon.match.color.three.puzzle.game"),
        ("Dialer", "com.icall.dialer_os.dialer"),
        ("iCaller Screen Dialer", "com.icaller.callscreen.dialer"),
        ("Lego Play", "com.lego.common.legoplay"),
        ("Lego Building Instructions", "com.lego.legobuildinginstructions"),
        ("Air Force Game", "com.os.airforce"),
        ("ABCmouse Academy", "mobi.abcmouse.academy_goo"),
        ("Basketball Shoot", "com.outthinking.basketballshoot"),
        ("Word Search", "in.playsimple.wordsearch"),
        ("Webmaster Game", "com.games.webmaster"),
        ("Runner Game", "com.creations.runnergame"),
        ("Rolling Sky Ball Balance", "com.bella.rolling.skyball.balance"),
        ("Noble Bingo Experience", "com.noble.bingo.experience"),
        ("Kids Coloring Book", "com.iz.coloring.games.kids.drawing.book.color.by.number"),
        ("Mega Ramp Ultimate Car Stunts", "com.fundrivegames.mega.ramp.ultimate.cars.stunts.impossibletracks"),
        ("Sky Rolling Ball Jump Adventure", "com.sky.rolling.ball.jump.balance.escape.adventure"),
        ("Kids Coloring Painting Learning", "com.iz.coloring.games.kids.drawing.color.book.painting.learning.baby.toddlers"),
        ("No Puzzle", "com.dxm.nopuzzle"),
        ("Prophet X Sweepstake", "com.prophetxsweepstake"),
        ("Sandwich Run", "jp.co.dwango.HcgDW007SandwichRun"),
        ("Garena Ball Run / Going Ball", "com.garena.ball.run.goingball.ironball.rollingball"),
        ("Pro Racer Driving in the City", "com.d20c.pro.racer.driving.in.the.city.game"),
        ("Space Force Galaxy Alien", "com.os.space.force.galaxy.alien"),
        ("Wheel Legend Speed Car", "com.wheel.legend.speed.car"),
        ("Bounce Dunk", "com.bounce.dunk"),
        ("Marvel HQ (StoryToys)", "com.storytoys.marvelhq.googleplay"),
        ("Traffic Driving Simulator", "com.bacon.zdb.traffic.driving.simulator"),
        ("Onstation", "com.projitech.onstation"),
        ("Sky Adventure Ball Game", "sky.adventure.ballgame"),
        ("Block Juggle", "com.block.juggle"),
        ("Race Master Stunt Drift Racing", "com.race.master.stunt.drift.racing.drive.free.car.games"),
        ("Aim Racing", "com.aim.racing"),
        ("Military Overturn", "games.vaveda.militaryoverturn"),
        ("Xuper TV", "com.blcksparrow.xupertv"),
        ("Blaze Shooter", "com.funfinity.amobear.blaze.shooter"),
        ("Drama Storymatrix", "com.storymatrix.drama"),
        ("Kwai Video", "com.kwai.video"),
        ("Xuper TV Series Finder", "com.t.finder.series.xupertv"),
        ("Linked Cubic", "io.supercent.linkedcubic"),
        ("Word Solitaire", "com.hitappsgames.wordsolitaire"),
        ("Royal Escape Kingdom Castle", "com.gamee.royal.escape.kingdom.castle.match.puzzle"),
        ("Run Gun", "com.kayac.rungun"),
        ("Pocket FM Radio", "com.radio.pocketfm"),
        ("Kredi Hesaplama", "com.pixelsdo.kredihesaplama"),
        ("Antistress Game", "com.zestplay.antistress"),
        ("Mob Control", "com.vincentb.MobControl"),
        ("NetShort Abroad", "com.netshort.abroad"),
        ("Video Maker Rey", "marketing.video.maker.rey"),
        ("AI Tutor Codeway", "com.codeway.aitutor"),
        ("PayPal", "com.paypal.android.p2pmobile"),
        ("Alien Shooter Galaxy Attack", "com.alien.shooter.galaxy.attack"),
        ("Volume Booster Speaker Louder", "volumebooster.soundspeaker.louder"),
        ("8 Ball Pool Miniclip", "com.miniclip.eightballpool"),
    ],
    "TCL & TracFone Bloatware": [
        ("TCL Guard / Optimizador", "com.tcl.guard"),
        ("TCL OneTouch Booster", "com.tct.onetouchbooster"),
        ("TCL Token", "com.tcl.token"),
        ("TCL Smart Miracast Control", "com.tct.smart.miracastcontrol"),
        ("TCL WFC Manager", "com.tct.gcs.wfcmanager"),
        ("TCL Setup Wizard", "com.tct.setupwizard"),
        ("TCL Screen Recorder", "com.tcl.screenrecorder"),
        ("TCL FM Radio", "com.tcl.fmradio"),
        ("TCL FOTA System", "com.tcl.fota.system"),
        ("TCL TTVS", "com.tcl.ttvs"),
        ("TCL E-Label", "com.jrdcom.Elabel"),
        ("TCL Secret Code", "com.tct.secretCode"),
        ("TCL GDPR / Privacidad", "com.tct.gdpr"),
        ("TCL System Service", "com.tct.systemservice"),
        ("TCL App Manager (AIO)", "com.tct.aio"),
        ("TCL Reduce SAR", "com.tct.reducesar"),
        ("TCL NXT Vision UI", "com.tct.nxtvision_ui"),
        ("TCL Smart NPS", "com.tct.smart.nps"),
        ("TCL Smart AOTA", "com.tct.smart.aota"),
        ("TCL APN Config", "com.tcl.tctapn"),
        ("TCL Msg Proxy", "com.tcl.tclmsgproxy"),
        ("TCL Theme Resources", "com.tct.tcltheme.resources"),
        ("TracFone / MySites", "com.tracfone.generic.mysites"),
        ("TracFone Preload Account Services", "com.tracfone.preload.accountservices"),
        ("TracFone DTI Downloader", "com.dti.tracfone"),
        ("TracFone Swishme", "com.swishme.tracfone"),
        ("App Lock Watcher", "com.domobile.applockwatcher"),
        ("Express Weather", "com.handmark.expressweather"),
        ("Gallery Albums Photo Manager", "com.gallery.albums.photomanager"),
        ("Android MMI Test (Pruebas)", "com.android.mmitest"),
        ("Silead Factory Test", "com.silead.factorytest"),
        ("FocalTech Fingerprint Test", "com.focaltech.fpsensormmitest"),
        ("Smart Manager Cleanup", "com.smartmanager.cleanup"),
        ("Puzzle Bricks Legend", "com.puzzlegames.puzzlebrickslegend"),
        ("Tiger (Huub)", "com.huub.tiger"),
        ("Lemon LV Overseas", "com.lemon.lvoverseas"),
        ("AI Art Photo Generator", "com.artorys.aiart.aiphotogenerator"),
        ("ShareIt / File Transfer", "apkshare.shareapps.filetransfer.shareit.bluetooth"),
        ("Passcode App", "com.kunkun.passcode"),
    ],
    "Redes Sociales y Apps Adicionales": [
        ("Instagram", "com.instagram.android"),
        ("Instagram Barcelona (Threads)", "com.instagram.barcelona"),
        ("LinkedIn", "com.linkedin.android"),
        ("X (Twitter)", "com.twitter.android"),
        ("Tinder", "com.tinder"),
        ("Facebook App", "com.facebook.katana"),
        ("Facebook Lite", "com.facebook.lite"),
        ("Facebook Services", "com.facebook.services"),
        ("Facebook App Manager", "com.facebook.appmanager"),
        ("Facebook System", "com.facebook.system"),
        ("ChatGPT", "com.openai.chatgpt"),
        ("Canva", "com.canva.editor"),
        ("Truth Social", "com.truthsocial.android.app"),
        ("Anchor / Spotify for Podcasters", "fm.anchor.android"),
        ("Microsoft Teams", "com.microsoft.teams"),
        ("Microsoft Outlook", "com.microsoft.office.outlook"),
    ],
    "Realidad Aumentada / AR": [
        ("AR Zone", "com.samsung.android.arzone"),
        ("AR Emoji", "com.samsung.android.aremoji"),
        ("AR Emoji Editor", "com.samsung.android.aremojieditor"),
        ("AR Drawing", "com.samsung.android.ardrawing"),
        ("Avatar Stickers", "com.sec.android.mimage.avatarstickers"),
    ],
    "Xiaomi / MIUI Bloatware & Ads": [
        ("Foro Global Xiaomi / BBS", "com.mi.global.bbs"),
        ("Mi Drop / ShareMe", "com.xiaomi.midrop"),
        ("WPS Office (Xiaomi Lite con anuncios)", "cn.wps.xiaomi.abroad.lite"),
        ("Escáner de Xiaomi", "com.xiaomi.scanner"),
        ("Grabadora de Pantalla MIUI", "com.miui.screenrecorder"),
        ("Mi Mover (Huanji)", "com.miui.huanji"),
        ("Editor de Medios MIUI", "com.miui.mediaeditor"),
        ("Tienda Global Xiaomi", "com.mi.global.shop"),
        ("Control Remoto Mi Remote", "com.duokan.phone.remotecontroller"),
        ("Carrusel de Fondos (Anuncios Lockscreen)", "com.miui.android.fashiongallery"),
        ("MIUI Analytics (Anuncios y datos)", "com.miui.analytics"),
        ("MIUI System Ads (MSA)", "com.miui.msa.global"),
        ("Xiaomi Daemon (Estadísticas)", "com.miui.daemon"),
        ("Huawei/Xiaomi DiagLogger", "com.huaqin.diaglogger"),
        ("Goodix GF Test (Huella)", "com.goodix.gftest"),
        ("Fingerprints Sensor Test", "com.fingerprints.sensortesttool"),
    ],
    "Servicios Cloud y Cuenta Xiaomi (Opcionales)": [
        ("Mi Cloud Service", "com.miui.cloudservice"),
        ("Mi Cloud Backup", "com.miui.cloudbackup"),
        ("Mi Cloud Sync", "com.miui.micloudsync"),
        ("Xiaomi Account", "com.xiaomi.account"),
        ("MiLink Service", "com.milink.service"),
    ],
    "Utilidades y Apps Secundarias de Xiaomi": [
        ("Páginas Amarillas MIUI", "com.miui.yellowpage"),
        ("Reporte de Errores", "com.miui.bugreport"),
        ("Limpiador Nativo MIUI", "com.miui.cleaner"),
        ("Xiaomi Discover (Recomendaciones)", "com.xiaomi.discover"),
        ("Mi Picks (Recomendaciones de apps)", "com.xiaomi.mipicks"),
        ("Game Turbo / Centro de Juegos", "com.xiaomi.glgm"),
        ("Frases del Teclado", "com.miui.phrase"),
        ("Procesamiento Extra de Fotos", "com.miui.extraphoto"),
        ("App Vault (Pantalla Izquierda)", "com.mi.globalminusscreen"),
        ("Mensajes Flotantes / Barra Juegos", "com.xiaomi.barrage"),
        ("Radio FM por software", "com.miui.fmservice"),
        ("Servicios y Soporte Xiaomi", "com.miui.miservice"),
        ("Notas de Xiaomi", "com.miui.notes"),
        ("Clima de Xiaomi", "com.miui.weather2"),
        ("Navegador Web de Xiaomi", "com.mi.globalbrowser"),
    ],
    "Streaming y Terceros": [
        ("Netflix", "com.netflix.mediaclient"),
        ("Amazon MP3", "com.amazon.mp3"),
        ("TikTok (Musically)", "com.zhiliaoapp.musically"),
        ("AliExpress", "com.alibaba.aliexpresshd"),
        ("WPS Office Completo", "cn.wps.moffice_eng"),
        ("Spotify", "com.spotify.music"),
        ("Pluto TV", "tv.pluto.android"),
        ("Buenovela", "com.fic.buenovela"),
    ],
    "Compras y Utilidades Adicionales": [
        ("Temu", "com.einnovation.temu"),
        ("Ubicación / Publicidad", "com.whfplus.location.ker"),
        ("Limpiador Ntoqa Clean", "com.cleaner.ntoqaclean.dock"),
        ("Limpiador Airof Manager", "com.clear.clean.airof.manager"),
        ("AliExpress / Alibaba", "com.alibaba.intl.android.apps.poseidon"),
        ("Amazon Prime Video", "com.amazon.avod.thirdpartyclient"),
        ("Amazon Shopping", "com.amazon.mShop.android.shopping"),
        ("Uber", "com.ubercab"),
        ("Uber Driver", "com.ubercab.driver"),
        ("PedidosYa", "com.pedidosya"),
        ("Headway Books", "com.headway.books"),
        ("Truecaller", "com.truecaller"),
        ("Duolingo", "com.duolingo"),
        ("CamScanner", "com.intsig.camscanner"),
        ("Zoom", "us.zoom.videomeetings"),
        ("Qik Banco Digital", "com.qik.android.app"),
        ("Banreservas Tu Banco", "com.banreservas.tubancoappmobile"),
        ("AFP Reservas", "com.afpreservas.appafpreservas"),
        ("ProUsuario", "com.prousuario.app"),
        ("DataCrédito Dominicana", "com.datacredito.midatamobile"),
        ("Banco BHD", "com.artech.infocorp_bhd.bhd"),
        ("EDENORTE", "es.indra.VMOEdeNorte"),
        ("EDESUR", "es.indra.VMOEdeEste"),
        ("DGII Móvil", "gov.dgii.dgiimovil"),
        ("Abogado M", "com.otbal.abogadom"),
        ("Cámaras IP Yoosee", "com.yoosee"),
        ("Cámaras EseeCloud", "com.juanvision.eseecloud30"),
        ("Cámaras USB / Endoscopios", "com.naxclow.v720"),
        ("Cámaras OTG", "com.ypcc.otgcamera"),
        ("Apple Tracker Detect", "com.apple.trackerdetect"),
        ("WhatsApp Web WhatScan", "whatsapp.web.whatscan.whatsweb.qrscan"),
        ("Cup Hero", "com.studio501.cuphero"),
        ("App de Terceros Genérica", "com.wdstechnology.android.kryten"),
    ]
}

CSC_MAP = {
    "DOR": "Altice / Tricom (LATAM / Caribe)", "TDR": "Altice / Tricom (LATAM / Caribe)", "TCN": "Altice / Tricom (LATAM / Caribe)",
    "ORR": "Orange (LATAM / Europa)", "ORA": "Orange (LATAM / Europa)",
    "CTM": "Claro (LATAM)", "CLO": "Claro (LATAM)", "AMX": "Claro (LATAM)", "CDR": "Claro (LATAM)",
    "ATT": "AT&T (EE. UU. / MX)", "CWH": "AT&T (EE. UU. / MX)", "TMM": "AT&T (EE. UU. / MX)",
    "TMO": "T-Mobile / Sprint (EE. UU.)", "TMK": "T-Mobile / Sprint (EE. UU.)", "SPR": "T-Mobile / Sprint (EE. UU.)",
    "VZW": "Verizon / Xfinity Mobile (EE. UU.)", "XAA": "Verizon / Xfinity Mobile (EE. UU.)", "CCT": "Verizon / Xfinity Mobile (EE. UU.)",
    "MOV": "Movistar / Telefonica (HISPAM)", "TEM": "Movistar / Telefonica (HISPAM)", "TLS": "Movistar / Telefonica (HISPAM)",
    "ZTM": "TIM (Brasil)", "TCE": "Telcel (México)"
}

# ==========================================
# VENTANA DE DEBUG (SOLO PARA DESARROLLO)
# ==========================================
class DebugWindow:
    def __init__(self, root):
        try:
            self.win = tk.Toplevel(root)
            self.win.title("🛠️ LOG DE DESARROLLO - MODO PRUEBA")
            self.win.geometry("700x400")
            self.win.protocol("WM_DELETE_WINDOW", self.hide)
            self.text = tk.Text(self.win, bg="#0d1117", fg="#58a6ff", font=("Consolas", 9), state="disabled")
            scroll = ttk.Scrollbar(self.win, orient="vertical", command=self.text.yview)
            self.text.configure(yscrollcommand=scroll.set)
            self.text.pack(side="left", fill="both", expand=True)
            scroll.pack(side="right", fill="y")
            btn_frame = tk.Frame(self.win)
            btn_frame.pack(side="bottom", fill="x", pady=2)
            tk.Button(btn_frame, text="📋 Copiar Log para Wolkelyn", command=self.copy_log, bg="#238636", fg="white").pack(side="right", padx=5)
            tk.Button(btn_frame, text="🗑️ Limpiar", command=self.clear_log).pack(side="left", padx=5)
        except:
            pass

    def log(self, tag, message):
        try:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log_line = f"[{timestamp}] [{tag}]\n{message}\n{'-'*50}\n"
            self.text.config(state="normal")
            self.text.insert(tk.END, log_line)
            self.text.see(tk.END)
            self.text.config(state="disabled")
        except:
            pass

    def copy_log(self):
        try:
            self.win.clipboard_clear()
            self.win.clipboard_append(self.text.get("1.0", tk.END))
            messagebox.showinfo("Copiado", "Log copiado. ¡Pásaselo a la IA para analizar!")
        except:
            pass

    def clear_log(self):
        try:
            self.text.config(state="normal")
            self.text.delete("1.0", tk.END)
            self.text.config(state="disabled")
        except:
            pass

    def hide(self):
        try:
            self.win.withdraw()
        except:
            pass

# ==========================================
# 2. MÓDULO DE OPTIMIZACIÓN Y REPORTE TÉCNICO
# ==========================================
class PhoneOptimizer:
    def __init__(self, adb_path="adb", debug_logger=None):
        self.adb_path = adb_path
        self.logger = debug_logger

    def run_adb(self, command, timeout=30):
        full_cmd = f'"{self.adb_path}" {command}'
        start_time = time.time()
        if self.logger: self.logger.log("ADB CMD SENT", full_cmd)
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=timeout, startupinfo=startupinfo)
            output = result.stdout.strip()
            duration = round(time.time() - start_time, 3)
            if self.logger: self.logger.log(f"ADB RESPONSE [{duration}s]", output if output else "<Sin salida / Success>")
            return output
        except subprocess.TimeoutExpired:
            duration = round(time.time() - start_time, 3)
            err_msg = f"Error: TimeoutExpired ({timeout}s)"
            if self.logger: self.logger.log(f"ADB TIMEOUT [{duration}s]", err_msg)
            return err_msg
        except Exception as e:
            duration = round(time.time() - start_time, 3)
            err_msg = f"Error: {str(e)}"
            if self.logger: self.logger.log(f"ADB ERROR [{duration}s]", err_msg)
            return err_msg

    def restart_adb_server(self):
        if self.logger: self.logger.log("ADB RESTART", "Ejecutando kill-server y start-server...")
        try:
            subprocess.run(f'"{self.adb_path}" kill-server', shell=True, capture_output=True)
            time.sleep(1)
            subprocess.run(f'"{self.adb_path}" start-server', shell=True, capture_output=True)
            time.sleep(1)
        except:
            pass

    def get_battery_status(self):
        try:
            output = self.run_adb("shell dumpsys battery")
            battery_info = {}
            for line in output.splitlines():
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        battery_info[parts[0].strip()] = parts[1].strip()
            return battery_info
        except:
            return {}
        
    def get_storage_stats(self, device_id):
        try:
            target = f"-s {device_id}" if device_id else ""
            out = self.run_adb(f"{target} shell df /data")
            for line in out.splitlines():
                if "/data" in line and not line.startswith("Filesystem"):
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            total_kb = int(parts[1].replace("K", "").replace("M", "").replace("G", ""))
                            used_kb = int(parts[2].replace("K", "").replace("M", "").replace("G", ""))
                            free_kb = int(parts[3].replace("K", "").replace("M", "").replace("G", ""))
                            if "G" in parts[1]: total_kb *= 1024 * 1024
                            elif "M" in parts[1]: total_kb *= 1024
                            if "G" in parts[2]: used_kb *= 1024 * 1024
                            elif "M" in parts[2]: used_kb *= 1024
                            if "G" in parts[3]: free_kb *= 1024 * 1024
                            elif "M" in parts[3]: free_kb *= 1024
                            
                            return total_kb // 1024, used_kb // 1024, free_kb // 1024
                        except:
                            pass
            
            out_m = self.run_adb(f"{target} shell df -m /data")
            for line in out_m.splitlines():
                if "/data" in line and not line.startswith("Filesystem"):
                    parts = line.split()
                    if len(parts) >= 4:
                        return int(parts[1]), int(parts[2]), int(parts[3])
        except:
            pass
        return 0, 0, 0

    def get_ram_stats(self, device_id):
        try:
            target = f"-s {device_id}" if device_id else ""
            out = self.run_adb(f"{target} shell cat /proc/meminfo")
            total_ram_mb = 0
            free_ram_mb = 0
            for line in out.splitlines():
                if "MemTotal:" in line:
                    try: total_ram_mb = int(line.split()[1]) // 1024
                    except: pass
                elif "MemAvailable:" in line or ("MemFree:" in line and free_ram_mb == 0):
                    try: free_ram_mb = int(line.split()[1]) // 1024
                    except: pass
            used_ram_mb = max(0, total_ram_mb - free_ram_mb)
            return total_ram_mb, used_ram_mb, free_ram_mb
        except:
            return 0, 0, 0

    def get_device_report(self, device_id):
        try:
            target = f"-s {device_id}" if device_id else ""
            model = self.run_adb(f"{target} shell getprop ro.product.model")
            brand = self.run_adb(f"{target} shell getprop ro.product.brand").capitalize()
            android_v = self.run_adb(f"{target} shell getprop ro.build.version.release")
            serial = self.run_adb(f"{target} shell getprop ro.serialno")
            batt = self.get_battery_status()
            batt_lvl = batt.get("level", "Desconocido")
            batt_health_code = batt.get("health", "N/A")
            if batt_health_code == "2": batt_health = "Buena (Good)"
            elif batt_health_code == "3": batt_health = "Sobrecalentada"
            elif batt_health_code == "4": batt_health = "Muerta / Reemplazar"
            else: batt_health = f"Código {batt_health_code}"
            df_out = self.run_adb(f"{target} shell df -h /data")
            storage_info = "Desconocido"
            for line in df_out.splitlines():
                if "/data" in line and not line.startswith("Filesystem"):
                    parts = line.split()
                    if len(parts) >= 4: storage_info = f"Total: {parts[1]} | Usado: {parts[2]} | Libre: {parts[3]}"
                    break
            
            report = f"📱 REPORTE TÉCNICO DEL DISPOSITIVO\n==================================\n\n"
            report += f"🔹 INFORMACIÓN GENERAL:\n   Marca: {brand}\n   Modelo: {model}\n   Android: {android_v}\n   SN: {serial}\n\n"
            report += f"🔋 ESTADO DE BATERÍA:\n   Nivel: {batt_lvl}%\n   Salud: {batt_health}\n   Voltaje: {batt.get('voltage', '0')} mV\n\n"
            report += f"💾 ALMACENAMIENTO:\n   {storage_info}\n==================================\n"
            return report
        except Exception as e:
            return f"Error generando reporte: {e}"

class GamerOptimizer:
    def __init__(self, optimizer_ref):
        self.optimizer = optimizer_ref

    def apply_profile(self, profile, device_id):
        target = f"-s {device_id}" if device_id else ""
        if profile == "turbo":
            self.optimizer.run_adb(f"{target} shell cmd power set-fixed-performance-mode-enabled true")
            self.optimizer.run_adb(f"{target} shell settings put system peak_refresh_rate 120.0")
            return "🚀 Modo Turbo aplicado con éxito (Rendimiento máximo y 120Hz)."
        elif profile == "balanced":
            self.optimizer.run_adb(f"{target} shell cmd power set-fixed-performance-mode-enabled false")
            return "⚖️ Rendimiento equilibrado aplicado."
        elif profile == "factory":
            self.optimizer.run_adb(f"{target} shell cmd power set-fixed-performance-mode-enabled false")
            self.optimizer.run_adb(f"{target} shell settings put global window_animation_scale 1.0")
            return "🏭 Valores originales restaurados."
        return "Perfil desconocido."

class CollapsiblePane(ttk.LabelFrame):
    def __init__(self, parent, title, *args, **kwargs):
        super().__init__(parent, text="", *args, **kwargs)
        self.is_open = False
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=1, pady=0)
        self.toggle_btn = ttk.Button(header_frame, text=f"▶ {title}", command=self.toggle, style="TButton")
        self.toggle_btn.pack(side="left", padx=1, fill="x", expand=True)
        self.title_text = title
        self.content_frame = ttk.Frame(self, padding=1)

    def toggle(self):
        if self.is_open:
            self.content_frame.pack_forget()
            self.toggle_btn.config(text=f"▶ {self.title_text}")
            self.is_open = False
        else:
            self.content_frame.pack(fill="x", expand=True, padx=2, pady=1)
            self.toggle_btn.config(text=f"▼ {self.title_text}")
            self.is_open = True

# ==========================================
# 4. INTERFAZ GRÁFICA PRINCIPAL
# ==========================================
class CleanPhoneApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"CleanPhone Pro v{CURRENT_VERSION} - Limpieza Inteligente By Wolkelyn")
        
        window_width = 720
        window_height = 780
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))

        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.resizable(True, True)
        self.root.minsize(720, 620)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", anchor="w")

        self.device_id = None
        self.device_serial = None
        self.check_vars = {}
        self.chk_widgets = {}
        self.carrier_sections = {}
        self.system_sections = {}
        self.is_processing = False
        self.cancel_requested = False
        
        self.pkg_to_name = {}
        self._build_pkg_translation_map()

        self.debug_win = DebugWindow(root)
        self.optimizer = PhoneOptimizer(debug_logger=self.debug_win)
        self.gamer_opt = GamerOptimizer(self.optimizer)
        self.backup_dir = os.path.join(os.getcwd(), "respaldos_cleanphone")

        header_container = tk.Frame(root)
        header_container.pack(fill="x", padx=8, pady=2)
        lbl_title = tk.Label(header_container, text=f"CleanPhone - Optimizador v{CURRENT_VERSION}", font=("Arial", 11, "bold"))
        lbl_title.pack(side="left", pady=2)
        
        self.btn_update_check = tk.Button(header_container, text="🔄 Actualizar", command=self.check_for_updates, bg="#6c757d", fg="white", font=("Arial", 8, "bold"))
        self.btn_update_check.pack(side="right", pady=2, padx=2)
        
        self.btn_salvame = tk.Button(header_container, text="💾 Sálvame mi app", command=self.open_salvame_modal, bg="#ffc107", fg="black", font=("Arial", 9, "bold"))
        self.btn_salvame.pack(side="right", pady=2, padx=10)

        info_frame = tk.LabelFrame(root, text=" Dispositivo Detectado ", padx=6, pady=2, font=("Arial", 9, "bold"))
        info_frame.pack(fill="x", padx=8, pady=2)
        self.lbl_info = tk.Label(info_frame, text="Esperando conexion USB...", justify="left", fg="gray", font=("Consolas", 9))
        self.lbl_info.pack(anchor="w", pady=0)
        btn_frame = tk.Frame(info_frame)
        btn_frame.pack(anchor="e", pady=2)
        self.btn_detect = tk.Button(btn_frame, text="Detectar Equipo", command=self.detect_device, bg="#007bff", fg="white", font=("Arial", 8, "bold"))
        self.btn_detect.pack(side="left", padx=2)
        self.btn_rescan = tk.Button(btn_frame, text="Redetectar Apps", command=self.scan_installed_apps_thread, bg="#17a2b8", fg="white", font=("Arial", 8, "bold"))
        self.btn_rescan.pack(side="left", padx=2)
        self.btn_report = tk.Button(btn_frame, text="📄 Reporte", command=self.show_tech_report, bg="#6f42c1", fg="white", font=("Arial", 8, "bold"))
        self.btn_report.pack(side="left", padx=2)
        self.btn_reboot = tk.Button(btn_frame, text="🔄 Reinicio", command=self.open_reboot_modal, bg="#343a40", fg="white", font=("Arial", 8, "bold"))
        self.btn_reboot.pack(side="left", padx=2)
        self.btn_toolbox = tk.Button(btn_frame, text="🧰 Herramientas", command=self.open_toolbox_modal, bg="#20c997", fg="white", font=("Arial", 8, "bold"))
        self.btn_toolbox.pack(side="left", padx=2)

        search_frame = tk.Frame(root)
        search_frame.pack(fill="x", padx=8, pady=4)
        tk.Label(search_frame, text="🔍 Buscar:", font=("Arial", 9, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_apps_live)
        self.entry_search = ttk.Entry(search_frame, textvariable=self.search_var, width=18)
        self.entry_search.pack(side="left", padx=4)

        tk.Label(search_frame, text=" | 📦 Custom Pkg:", font=("Arial", 9, "bold"), fg="#555").pack(side="left")
        self.custom_pkg_var = tk.StringVar()
        self.entry_custom_pkg = ttk.Entry(search_frame, textvariable=self.custom_pkg_var, width=22)
        self.entry_custom_pkg.pack(side="left", padx=4)
        self.btn_custom_delete = tk.Button(search_frame, text="Eliminar", bg="#dc3545", fg="white", font=("Arial", 8, "bold"), command=self.delete_custom_pkg)
        self.btn_custom_delete.pack(side="left", padx=2)

        frame_container = tk.Frame(root)
        frame_container.pack(fill="both", expand=True, padx=8, pady=2)
        self.canvas = tk.Canvas(frame_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.build_all_sections()

        progress_frame = tk.Frame(root)
        progress_frame.pack(fill="x", padx=10, pady=2)
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", side="top", padx=2, pady=1)
        self.lbl_progress_status = tk.Label(progress_frame, text="Estado: Listo", font=("Arial", 8), fg="gray")
        self.lbl_progress_status.pack(anchor="w", padx=2)

        monitor_frame = tk.LabelFrame(root, text=" Monitor de Procesos ", padx=6, pady=2, font=("Arial", 9, "bold"))
        monitor_frame.pack(fill="x", padx=8, pady=2)
        self.log_text = tk.Text(monitor_frame, height=3, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 8), state="disabled")
        log_scroll = ttk.Scrollbar(monitor_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")

        action_container = tk.Frame(root)
        action_container.pack(pady=4)

        row1_frame = tk.Frame(action_container)
        row1_frame.pack(pady=2)
        self.btn_debloat = tk.Button(row1_frame, text="🗑️ DESINSTALAR", bg="#dc3545", fg="white", font=("Arial", 8, "bold"), command=self.execute_debloat, width=15, pady=4)
        self.btn_debloat.pack(side="left", padx=4)
        
        self.btn_restore = tk.Button(row1_frame, text="📦 RESPALDAR DATOS", bg="#28a745", fg="white", font=("Arial", 8, "bold"), command=self.execute_data_backup, width=16, pady=4)
        self.btn_restore.pack(side="left", padx=4)
        
        self.btn_gamer = tk.Button(row1_frame, text="🎮 MODO GAMER", bg="#6f42c1", fg="white", font=("Arial", 8, "bold"), command=self.open_gamer_modal, width=15, pady=4)
        self.btn_gamer.pack(side="left", padx=4)

        row2_frame = tk.Frame(action_container)
        row2_frame.pack(pady=2)
        self.btn_cache = tk.Button(row2_frame, text="🧹 LIMPIEZA CACHÉ PROFUNDA", bg="#17a2b8", fg="white", font=("Arial", 8, "bold"), command=self.execute_cache_cleaning, width=24, pady=4)
        self.btn_cache.pack(side="left", padx=4)
        self.btn_optimize = tk.Button(row2_frame, text="⚡ OPTIMIZAR (KERNEL & DB)", bg="#fd7e14", fg="white", font=("Arial", 8, "bold"), command=self.execute_system_optimization, width=24, pady=4)
        self.btn_optimize.pack(side="left", padx=4)

        self.detect_device()

    def _build_pkg_translation_map(self):
        for carrier, items in CARRIER_BLOATWARE.items():
            for name, pkg in items:
                self.pkg_to_name[pkg] = name
        for cat, items in SYSTEM_BLOATWARE.items():
            for name, pkg in items:
                self.pkg_to_name[pkg] = name

    def check_for_updates(self):
        self.log("Buscando actualizaciones...")
        try:
            req = urllib.request.Request(VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
            remote_version = data.get("version")
            changelog = data.get("changelog", "Sin notas.")
            download_url = data.get("download_url")
            
            if remote_version and remote_version != CURRENT_VERSION:
                if messagebox.askyesno("Actualización", f"Nueva versión ({remote_version}) disponible.\n\n{changelog}\n\n¿Instalar ahora?"):
                    self.download_and_apply_update(download_url)
            else:
                messagebox.showinfo("Actualización", f"Ya tienes la última versión (v{CURRENT_VERSION}).")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar actualización: {e}")

    def download_and_apply_update(self, url):
        try:
            current_exe = os.path.abspath(sys.argv[0])
            temp_exe = current_exe + ".new"
            urllib.request.urlretrieve(url, temp_exe)
            bat_path = os.path.join(os.path.dirname(current_exe), "update.bat")
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(f'@echo off\ntimeout /t 2 /nobreak > nul\ndel "{current_exe}"\nmove "{temp_exe}" "{current_exe}"\nstart "" "{current_exe}"\ndel "%~f0"\n')
            subprocess.Popen(bat_path, shell=True)
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al actualizar: {e}")

    def open_gamer_modal(self):
        if not self.device_id: return messagebox.showerror("Error", "No hay teléfono conectado.")
        win = tk.Toplevel(self.root)
        win.title("Modo Gamer")
        win.geometry("380x260")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        tk.Label(win, text="🎮 Selector de Perfil Gamer", font=("Arial", 10, "bold")).pack(pady=10)
        tk.Button(win, text="🚀 Modo Turbo (FPS Máximos)", bg="#d9534f", fg="white", font=("Arial", 9, "bold"), width=32, pady=5, command=lambda: [self.apply_gamer("turbo"), win.destroy()]).pack(pady=5)
        tk.Button(win, text="⚖️ Rendimiento Equilibrado", bg="#f0ad4e", fg="white", font=("Arial", 9, "bold"), width=32, pady=5, command=lambda: [self.apply_gamer("balanced"), win.destroy()]).pack(pady=5)
        tk.Button(win, text="🏭 Fábrica (Original)", bg="#5bc0de", fg="white", font=("Arial", 9, "bold"), width=32, pady=5, command=lambda: [self.apply_gamer("factory"), win.destroy()]).pack(pady=5)

    def apply_gamer(self, profile):
        res_msg = self.gamer_opt.apply_profile(profile, self.device_id)
        messagebox.showinfo("Modo Gamer", res_msg)

    def open_salvame_modal(self):
        if not self.device_id or not self.device_serial:
            return messagebox.showerror("Error", "No hay teléfono conectado para salvar.")
            
        dev_backup_dir = os.path.join(self.backup_dir, self.device_serial)
        backup_file = os.path.join(dev_backup_dir, "backup.json")
        
        if not os.path.exists(backup_file):
            return messagebox.showwarning("Sin Respaldos", f"No encontré ningún respaldo guardado para este equipo (Serial: {self.device_serial}).")
            
        win = tk.Toplevel(self.root)
        win.title("CleanPhone Pro - Sálvame mi app")
        win.geometry("420x220")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        
        tk.Label(win, text="💾 Sálvame mi app (Restauración)", font=("Arial", 10, "bold"), fg="darkblue").pack(pady=8)
        tk.Label(win, text="claro hijo mío, Pero deja de ser pendejo y solo elimina lo que conoces", font=("Arial", 8, "italic"), fg="#d9534f", wraplength=380, justify="center").pack(pady=2)
        
        def run_all():
            win.destroy()
            try:
                with open(backup_file, "r") as f:
                    data = json.load(f)
                target_pkgs = list(data.keys())
            except:
                target_pkgs = []
            if target_pkgs:
                self._open_live_progress_window(backup_file, target_pkgs)
            
        def run_select():
            win.destroy()
            self._open_salvame_selector(backup_file)

        tk.Button(win, text="⚡ Restaurar TODO Automáticamente", bg="#28a745", fg="white", font=("Arial", 9, "bold"), width=35, pady=5, command=run_all).pack(pady=6)
        tk.Button(win, text="📋 Elegir qué aplicaciones restaurar", bg="#17a2b8", fg="white", font=("Arial", 9, "bold"), width=35, pady=5, command=run_select).pack(pady=4)

    def _open_salvame_selector(self, backup_file):
        try:
            with open(backup_file, "r") as f:
                data = json.load(f)
        except Exception as e:
            return messagebox.showerror("Error", f"No se pudo leer el respaldo: {e}")
            
        if not data:
            return messagebox.showwarning("Vacío", "El archivo de respaldo no contiene aplicaciones registradas.")

        sel_win = tk.Toplevel(self.root)
        sel_win.title("Sálvame mi app - Seleccionar Aplicaciones")
        sel_win.geometry("480x460")
        sel_win.resizable(False, False)
        sel_win.transient(self.root)
        sel_win.grab_set()

        tk.Label(sel_win, text="Selecciona las aplicaciones que deseas rescatar:", font=("Arial", 9, "bold")).pack(pady=8)
        
        canvas_frame = tk.Frame(sel_win)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=2)
        
        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        app_vars = {}
        for pkg, info in data.items():
            var = tk.BooleanVar(value=True)
            human_name = self.pkg_to_name.get(pkg, pkg) # Solo muestra el nombre amigable (ej. Google Maps) sin el paquete técnico
            chk = tk.Checkbutton(scroll_frame, text=human_name, variable=var, anchor="w", font=("Arial", 9))
            chk.pack(fill="x", anchor="w", padx=6, pady=3)
            app_vars[pkg] = var

        def confirm_selection():
            selected_pkgs = [pkg for pkg, var in app_vars.items() if var.get()]
            sel_win.destroy()
            if not selected_pkgs:
                return messagebox.showwarning("Atención", "No seleccionaste ninguna aplicación.")
            self._open_live_progress_window(backup_file, selected_pkgs)

        # Contenedor inferior para centrar perfectamente el botón de restaurar
        bottom_frame = tk.Frame(sel_win)
        bottom_frame.pack(fill="x", pady=12)
        
        btn_confirm = tk.Button(bottom_frame, text="✅ Restaurar Seleccionadas", bg="#28a745", fg="white", font=("Arial", 10, "bold"), width=28, pady=6, command=confirm_selection)
        btn_confirm.pack(anchor="center")

    def _open_live_progress_window(self, backup_file, target_pkgs):
        self.toggle_buttons(True)
        self.cancel_requested = False
        
        prog_win = tk.Toplevel(self.root)
        prog_win.title("CleanPhone Pro - Sálvame mi app en Vivo")
        prog_win.geometry("460x250")
        prog_win.resizable(False, False)
        prog_win.transient(self.root)
        prog_win.grab_set()

        tk.Label(prog_win, text="🔄 PROCESO DE RESTAURACIÓN ACTIVO", font=("Arial", 10, "bold"), fg="darkblue").pack(pady=10)
        
        lbl_current_title = tk.Label(prog_win, text="Aplicando a:", font=("Arial", 8), fg="gray")
        lbl_current_title.pack(anchor="w", padx=20)
        
        lbl_app_name = tk.Label(prog_win, text="Iniciando...", font=("Arial", 11, "bold"), fg="#333")
        lbl_app_name.pack(anchor="w", padx=20, pady=2)

        pb_var = tk.DoubleVar(value=0.0)
        pb = ttk.Progressbar(prog_win, orient="horizontal", mode="determinate", variable=pb_var, maximum=100)
        pb.pack(fill="x", padx=20, pady=10)

        lbl_status_text = tk.Label(prog_win, text="Estado: Preparando...", font=("Arial", 8), fg="gray")
        lbl_status_text.pack(anchor="w", padx=20)

        def request_cancel():
            self.cancel_requested = True
            self.log("¡Cancelación solicitada por el usuario!")
            try:
                lbl_status_text.config(text="Estado: Cancelando proceso...")
            except:
                pass

        btn_cancel = tk.Button(prog_win, text="❌ Cancelar Proceso y Reiniciar ADB", bg="#dc3545", fg="white", font=("Arial", 9, "bold"), command=request_cancel)
        btn_cancel.pack(pady=10)

        def worker_logic():
            self.log("--- INICIANDO PROTOCOLO SÁLVAME MI APP ---")
            try:
                with open(backup_file, "r") as f:
                    data = json.load(f)
                
                exito_instalacion = []
                exito_habilitacion = []
                fallidos = []

                total = max(1, len(target_pkgs))
                for i, pkg in enumerate(target_pkgs):
                    if self.cancel_requested:
                        break
                    if pkg not in data: continue
                    
                    info = data[pkg]
                    action = info.get("action")
                    human_name = self.pkg_to_name.get(pkg, pkg)
                    
                    percent = int((i / total) * 100)
                    
                    def update_ui_safe(p, n, idx):
                        try:
                            if prog_win.winfo_exists():
                                pb_var.set(p)
                                lbl_app_name.config(text=n)
                                lbl_status_text.config(text=f"Procesando ({idx+1}/{total})...")
                                prog_win.update_idletasks()
                        except:
                            pass

                    prog_win.after(0, update_ui_safe, percent, human_name, i)
                    
                    if action == "disabled":
                        res = self.run_adb(f"-s {self.device_id} shell pm enable --user 0 {pkg}", timeout=15)
                        if "New state" in res or "already enabled" in res or not res:
                            exito_habilitacion.append(human_name)
                            self.log(f"Rehabilitada con éxito: {pkg}")
                        else:
                            fallidos.append(f"{human_name} (No se pudo habilitar)")
                            self.log(f"Error al habilitar {pkg}: {res}")
                            
                    elif action == "uninstalled":
                        apk_path = info.get("apk")
                        if apk_path and os.path.exists(apk_path):
                            instalado_ok = False
                            self.log(f"Instalando APK (Intento 1/2): {pkg}...")
                            res_inst = self.run_adb(f'-s {self.device_id} install -r "{apk_path}"', timeout=30)
                            if "Success" in res_inst:
                                instalado_ok = True
                            else:
                                self.log(f"Intento 1 fallido para {pkg}. Reiniciando servidor ADB...")
                                self.optimizer.restart_adb_server()
                                time.sleep(2)
                                
                                self.log(f"Instalando APK (Intento 2/2): {pkg}...")
                                res_inst2 = self.run_adb(f'-s {self.device_id} install -r "{apk_path}"', timeout=35)
                                if "Success" in res_inst2:
                                    instalado_ok = True
                                else:
                                    self.log(f"Intento 2 fallido para {pkg}. Reiniciando servidor ADB de nuevo...")
                                    self.optimizer.restart_adb_server()
                                    time.sleep(2)

                            if instalado_ok:
                                exito_instalacion.append(human_name)
                                self.log(f"Reinstalada (APK local): {pkg}")
                            else:
                                fallidos.append(f"{human_name} (Timeout o Error)")
                                self.log(f"Fallo definitivo instalando {pkg}")
                        else:
                            res = self.run_adb(f"-s {self.device_id} shell cmd package install-existing {pkg}", timeout=20)
                            if "Installed" in res or not res:
                                exito_instalacion.append(human_name)
                                self.log(f"Reinstalada (Usuario): {pkg}")
                            else:
                                fallidos.append(f"{human_name} (No disponible en ROM)")
                                
                try:
                    prog_win.after(0, lambda: prog_win.destroy())
                except:
                    pass

                self.log("--- PROTOCOLO SÁLVAME MI APP FINALIZADO ---")
                self.root.after(0, self.detect_device)
                
                if self.cancel_requested:
                    self.optimizer.restart_adb_server()
                    reporte_str = "Proceso cancelado por el usuario. Se ha reiniciado el servicio ADB."
                else:
                    reporte_str = f"=== INFORME DE SÁLVAME MI APP ===\n" \
                                  f"✅ Apps Instaladas: {len(exito_instalacion)}\n" \
                                  f"☑️ Apps Habilitadas: {len(exito_habilitacion)}\n" \
                                  f"❌ Fallidas / Omitidas: {len(fallidos)}"
                self.root.after(0, lambda: messagebox.showinfo("Informe de Sálvame mi app", reporte_str))
                
            except Exception as e:
                self.log(f"Error en Sálvame mi app: {e}")
                self.optimizer.restart_adb_server()
                try:
                    prog_win.after(0, lambda: prog_win.destroy())
                except:
                    pass
                self.root.after(0, lambda: messagebox.showerror("Error", f"Ocurrió un error al restaurar: {e}"))
                
            self.root.after(0, lambda: self.toggle_buttons(False))
            self.root.after(2000, lambda: self.update_progress(0, "Listo"))

        threading.Thread(target=worker_logic, daemon=True).start()

    def execute_data_backup(self):
        if not self.device_id or not self.device_serial:
            return messagebox.showerror("Error", "No hay teléfono conectado para respaldar datos.")
            
        dev_backup_dir = os.path.join(self.backup_dir, self.device_serial)
        os.makedirs(dev_backup_dir, exist_ok=True)
        backup_path = os.path.join(dev_backup_dir, "datos_personales.ab")

        msg = "⚠️ ATENCIÓN:\n\nMira la pantalla de tu teléfono ahora mismo.\nDesbloquéalo y acepta la solicitud de copia de seguridad de datos personales (WhatsApp y Contactos).\n\n¿Estás listo para continuar?"
        if not messagebox.askyesno("Respaldo de Datos", msg):
            return

        self.toggle_buttons(True)
        self.log("--- INICIANDO RESPALDO DE DATOS DE USUARIO ---")
        
        def worker():
            cmd = f'-s {self.device_id} backup -f "{backup_path}" -noapk com.whatsapp com.android.providers.contacts'
            self.run_adb(cmd, timeout=120)
            
            if os.path.exists(backup_path) and os.path.getsize(backup_path) > 1024:
                self.log(f"Respaldo de datos guardado con éxito en: {backup_path}")
                self.root.after(0, lambda: messagebox.showinfo("Éxito", f"Copia de seguridad de datos completada.\nGuardado en:\n{backup_path}"))
            else:
                self.log("El respaldo de datos fue cancelado o no generó contenido.")
                self.root.after(0, lambda: messagebox.showwarning("Aviso", "El respaldo no se completó o fue cancelado desde el dispositivo."))
                
            self.root.after(0, lambda: self.toggle_buttons(False))

        threading.Thread(target=worker, daemon=True).start()

    def open_toolbox_modal(self):
        if not self.device_id: return messagebox.showerror("Error", "No hay teléfono conectado.")
        win = tk.Toplevel(self.root)
        win.title("Caja de Herramientas del Técnico")
        win.geometry("400x340")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="🧰 Utilidades Rápidas", font=("Arial", 10, "bold")).pack(pady=10)
        
        def install_apk():
            filepath = filedialog.askopenfilename(filetypes=[("Archivos APK", "*.apk")], title="Seleccionar APK para instalar")
            if not filepath: return
            self.log(f"Instalando APK: {os.path.basename(filepath)}...")
            messagebox.showinfo("Instalando", "La instalación ha comenzado. Espera unos minutos.")
            def worker():
                res = self.run_adb(f'-s {self.device_id} install "{filepath}"', timeout=60)
                if "Success" in res: self.root.after(0, lambda: messagebox.showinfo("Éxito", "Instalado correctamente."))
                else: self.root.after(0, lambda: messagebox.showerror("Error", f"No se pudo instalar:\n{res}"))
            threading.Thread(target=worker, daemon=True).start()
        
        tk.Button(win, text="📥 Instalar APK desde PC (Sideload)", bg="#28a745", fg="white", font=("Arial", 9, "bold"), width=35, pady=5, command=install_apk).pack(pady=5)
        tk.Button(win, text="🌐 Abrir Navegador (Helper FRP)", bg="#007bff", fg="white", font=("Arial", 9, "bold"), width=35, pady=5, command=lambda: self.run_adb(f"-s {self.device_id} shell am start -a android.intent.action.VIEW -d 'https://www.google.com'")).pack(pady=5)
        tk.Button(win, text="🌙 Forzar Modo Oscuro", bg="#343a40", fg="white", font=("Arial", 9, "bold"), width=35, pady=5, command=lambda: self.run_adb(f"-s {self.device_id} shell cmd uimode night yes")).pack(pady=5)
        tk.Button(win, text="☀️ Forzar Modo Claro", bg="#f8f9fa", fg="black", font=("Arial", 9, "bold"), width=35, pady=5, command=lambda: self.run_adb(f"-s {self.device_id} shell cmd uimode night no")).pack(pady=5)
        tk.Button(win, text="📱 Restablecer Pantalla (DPI de Fábrica)", bg="#17a2b8", fg="white", font=("Arial", 9, "bold"), width=35, pady=5, command=lambda: self.run_adb(f"-s {self.device_id} shell wm density reset")).pack(pady=5)

    def open_reboot_modal(self):
        if not self.device_id: return messagebox.showerror("Error", "No hay teléfono conectado.")
        win = tk.Toplevel(self.root)
        win.title("Opciones de Reinicio")
        win.geometry("380x280")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        tk.Label(win, text="🔄 Menú de Reinicio Avanzado", font=("Arial", 10, "bold")).pack(pady=10)
        tk.Button(win, text="🔄 Reinicio Normal", bg="#007bff", fg="white", font=("Arial", 9, "bold"), width=32, pady=5, command=lambda: [self.run_adb(f"-s {self.device_id} reboot"), win.destroy()]).pack(pady=5)
        tk.Button(win, text="🛠️ Modo Recovery", bg="#dc3545", fg="white", font=("Arial", 9, "bold"), width=32, pady=5, command=lambda: [self.run_adb(f"-s {self.device_id} reboot recovery"), win.destroy()]).pack(pady=5)
        tk.Button(win, text="⬇️ Modo Bootloader / Download", bg="#ffc107", fg="black", font=("Arial", 9, "bold"), width=32, pady=5, command=lambda: [self.run_adb(f"-s {self.device_id} reboot bootloader"), win.destroy()]).pack(pady=5)
        tk.Button(win, text="🛑 Apagar Equipo", bg="#343a40", fg="white", font=("Arial", 9, "bold"), width=32, pady=5, command=lambda: [self.run_adb(f"-s {self.device_id} shell reboot -p"), win.destroy()]).pack(pady=5)

    def show_tech_report(self):
        if not self.device_id: return messagebox.showerror("Error", "No hay teléfono conectado.")
        self.log("Generando reporte técnico...")
        report_str = self.optimizer.get_device_report(self.device_id)
        win = tk.Toplevel(self.root)
        win.title("Reporte Técnico del Dispositivo")
        win.geometry("450x420")
        win.transient(self.root)
        win.grab_set()
        txt = tk.Text(win, bg="#f8f9fa", font=("Consolas", 10), padx=10, pady=10)
        txt.pack(fill="both", expand=True, padx=5, pady=5)
        txt.insert(tk.END, report_str)
        txt.config(state="disabled")

    def filter_apps_live(self, *args):
        try:
            query = self.search_var.get().lower()
            for pkg, chk in self.chk_widgets.items():
                text = chk.cget("text").lower()
                if query in text or query in pkg.lower(): chk.pack(fill="x", anchor="w", padx=4, pady=0)
                else: chk.pack_forget()
        except:
            pass

    def toggle_buttons(self, state):
        try:
            btn_state = tk.DISABLED if state else tk.NORMAL
            self.btn_debloat.config(state=btn_state)
            self.btn_restore.config(state=btn_state) 
            self.btn_gamer.config(state=btn_state)
            self.btn_cache.config(state=btn_state)
            self.btn_optimize.config(state=btn_state)
            self.btn_custom_delete.config(state=btn_state)
            self.btn_report.config(state=btn_state)
            self.btn_reboot.config(state=btn_state)
            self.btn_toolbox.config(state=btn_state)
            self.btn_salvame.config(state=btn_state)
            self.btn_update_check.config(state=btn_state)
            self.btn_detect.config(state=btn_state)
            self.btn_rescan.config(state=btn_state)
            self.is_processing = state
        except:
            pass

    def log(self, message):
        try:
            self.log_text.config(state="normal")
            self.log_text.insert(tk.END, f"> {message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state="disabled")
        except:
            pass

    def update_progress(self, val, text=""):
        try:
            self.progress_var.set(val)
            if text: self.lbl_progress_status.config(text=f"Estado: {text} ({int(val)}%)")
        except:
            pass

    def on_canvas_configure(self, event):
        try:
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        except:
            pass

    def run_adb(self, cmd, timeout=30):
        return self.optimizer.run_adb(cmd, timeout=timeout)

    def detect_device(self):
        self.log("Buscando dispositivos conectados...")
        def worker():
            try:
                devices_out = self.run_adb("devices")
                lines = [l for l in devices_out.split("\n")[1:] if "device" in l]

                if not lines:
                    def update_no_dev():
                        try:
                            self.device_id = None
                            self.device_serial = None
                            self.lbl_info.config(text="Estado: Ningun dispositivo detectado. Conecta el USB y activa Depuracion.", fg="red")
                            self.log("Ningún dispositivo detectado.")
                            self.update_visible_sections("", "")
                        except:
                            pass
                    self.root.after(0, update_no_dev)
                    return

                dev_id = lines[0].split()[0]
                dev_serial = self.run_adb(f"-s {dev_id} shell getprop ro.serialno").strip()
                model = self.run_adb(f"-s {dev_id} shell getprop ro.product.model")
                brand = self.run_adb(f"-s {dev_id} shell getprop ro.product.brand").capitalize()
                carrier_csc = self.run_adb(f"-s {dev_id} shell getprop ro.csc.sales_code").upper()
                detected_carrier = CSC_MAP.get(carrier_csc, "")

                tot_stor, used_stor, free_stor = self.optimizer.get_storage_stats(dev_id)
                tot_ram, used_ram, free_ram = self.optimizer.get_ram_stats(dev_id)

                stor_str = f"{round(used_stor/1024, 1)}GB Usado / {round(free_stor/1024, 1)}GB Libre (Tot: {round(tot_stor/1024, 1)}GB)" if tot_stor > 0 else "N/A"
                ram_str = f"{used_ram}MB Usado / {free_ram}MB Libre (Tot: {tot_ram}MB)" if tot_ram > 0 else "N/A"

                info_text = f"📱 {brand} {model} | Operadora: {detected_carrier or 'Libre / Genérica'}\n💾 Almacenamiento: {stor_str}\n🧠 Memoria RAM: {ram_str}"

                def update_yes_dev():
                    try:
                        self.device_id = dev_id
                        self.device_serial = dev_serial
                        self.lbl_info.config(text=info_text, fg="darkblue")
                        self.log(f"Dispositivo detectado: {self.device_id} (SN: {self.device_serial})")
                        self.update_visible_sections(detected_carrier, brand)
                        self.scan_installed_apps_thread()
                    except:
                        pass

                self.root.after(0, update_yes_dev)
            except Exception as e:
                self.log(f"Error detectando equipo: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def get_installed_packages(self):
        if not self.device_id: return set()
        output = self.run_adb(f"-s {self.device_id} shell pm list packages")
        return {line.replace("package:", "").strip().lower() for line in output.splitlines() if line.startswith("package:")}

    def scan_installed_apps_thread(self):
        if not self.device_id: return
        threading.Thread(target=self.scan_installed_apps, daemon=True).start()

    def scan_installed_apps(self):
        try:
            installed_packages = self.get_installed_packages()
            count = 0
            def update_ui():
                nonlocal count
                try:
                    for pkg, var in self.check_vars.items():
                        if pkg.lower() in installed_packages:
                            var.set(True)
                            count += 1
                            if pkg in self.chk_widgets: self.chk_widgets[pkg].config(fg="black", font=("Arial", 9, "bold"))
                        else:
                            var.set(False)
                            if pkg in self.chk_widgets: self.chk_widgets[pkg].config(fg="gray", font=("Arial", 9))
                    self.log(f"Escaneo finalizado. {count} apps instaladas detectadas.")
                except:
                    pass
            self.root.after(0, update_ui)
        except Exception as e:
            self.log(f"Error escaneando apps: {e}")

    def _set_group_selection(self, group_vars, state):
        for var in group_vars.values(): var.set(state)

    def build_all_sections(self):
        for carrier, items in CARRIER_BLOATWARE.items():
            pane = CollapsiblePane(self.scrollable_frame, f"Operadora: {carrier} ({len(items)} apps)")
            self.carrier_sections[carrier] = pane
            ctrl_frame = tk.Frame(pane.content_frame)
            ctrl_frame.pack(fill="x", padx=4, pady=2)
            group_vars = {}
            tk.Button(ctrl_frame, text="☑ Marcar Todo", command=lambda v=group_vars: self._set_group_selection(v, True), font=("Arial", 7), bg="#495057", fg="white", pady=0).pack(side="left", padx=2)
            tk.Button(ctrl_frame, text="☒ Desmarcar Todo", command=lambda v=group_vars: self._set_group_selection(v, False), font=("Arial", 7), bg="#495057", fg="white", pady=0).pack(side="left", padx=2)
            for name, pkg in items:
                var = tk.BooleanVar(value=False)
                chk = tk.Checkbutton(pane.content_frame, text=f"{name} [{pkg}]", variable=var, anchor="w", justify="left")
                chk.pack(fill="x", anchor="w", padx=4, pady=0)
                self.check_vars[pkg] = var
                self.chk_widgets[pkg] = chk
                group_vars[pkg] = var

        for cat_name, items in SYSTEM_BLOATWARE.items():
            display_name = "Apps que envían información sin permiso" if "Xiaomi" in cat_name else "App Basura: " + cat_name
            pane = CollapsiblePane(self.scrollable_frame, f"{display_name} ({len(items)} apps)")
            self.system_sections[cat_name] = pane
            ctrl_frame = tk.Frame(pane.content_frame)
            ctrl_frame.pack(fill="x", padx=4, pady=2)
            group_vars = {}
            tk.Button(ctrl_frame, text="☑ Marcar Todo", command=lambda v=group_vars: self._set_group_selection(v, True), font=("Arial", 7), bg="#495057", fg="white", pady=0).pack(side="left", padx=2)
            tk.Button(ctrl_frame, text="☒ Desmarcar Todo", command=lambda v=group_vars: self._set_group_selection(v, False), font=("Arial", 7), bg="#495057", fg="white", pady=0).pack(side="left", padx=2)
            for name, pkg in items:
                var = tk.BooleanVar(value=False)
                chk = tk.Checkbutton(pane.content_frame, text=f"{name} [{pkg}]", variable=var, anchor="w", justify="left")
                chk.pack(fill="x", anchor="w", padx=4, pady=0)
                self.check_vars[pkg] = var
                self.chk_widgets[pkg] = chk
                group_vars[pkg] = var

    def update_visible_sections(self, carrier, brand=""):
        try:
            for pane in self.carrier_sections.values(): pane.pack_forget()
            for pane in self.system_sections.values(): pane.pack_forget()
            if carrier and carrier in self.carrier_sections: self.carrier_sections[carrier].pack(fill="x", expand=True, pady=1)

            brand = brand.lower()
            for cat_name, pane in self.system_sections.items():
                cat_lower = cat_name.lower()
                es_samsung = "samsung" in cat_lower or "realidad aumentada" in cat_lower
                es_xiaomi = "xiaomi" in cat_lower or "miui" in cat_lower
                es_tcl = "tcl" in cat_lower
                mostrar = True
                
                if es_samsung and "samsung" not in brand: mostrar = False
                elif es_xiaomi and not any(x in brand for x in ["xiaomi", "redmi", "poco"]): mostrar = False
                elif es_tcl and "tcl" not in brand: mostrar = False
                if mostrar: pane.pack(fill="x", expand=True, pady=1)
        except:
            pass

    def execute_cache_cleaning(self):
        if not self.device_id: return messagebox.showerror("Error", "No hay teléfono conectado.")
        if self.is_processing: return messagebox.showwarning("Espera", "Proceso activo.")
        if not messagebox.askyesno("Confirmar", "¿Ejecutar limpieza de Caché Profunda y Logs Temporales?"): return
        self.toggle_buttons(True)
        threading.Thread(target=self._run_cache_worker, daemon=True).start()

    def _run_cache_worker(self):
        self.log("--- INICIANDO LIMPIEZA DE CACHÉ PROFUNDA ---")
        _, _, free_antes = self.optimizer.get_storage_stats(self.device_id)
        
        self.root.after(0, self.update_progress, 30, "Vaciando Cachés de Apps (Sin borrar datos)")
        self.optimizer.run_adb(f"-s {self.device_id} shell pm trim-caches 999999999999999999", timeout=60)
        
        self.root.after(0, self.update_progress, 60, "Borrando Registros Locales del Sistema (Logs)")
        self.optimizer.run_adb(f"-s {self.device_id} shell rm -rf /data/local/tmp/*", timeout=20)
        
        self.root.after(0, self.update_progress, 100, "Calculando espacio liberado...")
        
        _, _, free_despues = self.optimizer.get_storage_stats(self.device_id)
        ganancia_mb = max(0, free_despues - free_antes)
        ganancia_gb = round(ganancia_mb / 1024, 2)
        
        self.log(f"--- LIMPIEZA FINALIZADA (Liberados: {ganancia_gb} GB) ---")
        self.root.after(0, lambda: messagebox.showinfo("Éxito", f"Limpieza finalizada.\n\nLiberaste {ganancia_gb} GB de espacio basura."))
        self.root.after(0, lambda: self.toggle_buttons(False))
        self.root.after(0, self.detect_device)
        self.root.after(2000, lambda: self.update_progress(0, "Listo"))

    def execute_system_optimization(self):
        if not self.device_id: return messagebox.showerror("Error", "No hay teléfono conectado.")
        if self.is_processing: return messagebox.showwarning("Espera", "Proceso activo.")
        if not messagebox.askyesno("Confirmar", "¿Ejecutar optimización avanzada (Kernel, Bases de datos SQLite y Animaciones)?"): return
        self.toggle_buttons(True)
        threading.Thread(target=self._run_optimization_worker, daemon=True).start()

    def _run_optimization_worker(self):
        self.log("--- INICIANDO OPTIMIZACIÓN AVANZADA ---")
        self.root.after(0, self.update_progress, 20, "Ajustando Animaciones y Telemetría")
        self.optimizer.run_adb(f"-s {self.device_id} shell settings put global window_animation_scale 0.85", timeout=10)
        self.optimizer.run_adb(f"-s {self.device_id} shell settings put global transition_animation_scale 0.85", timeout=10)
        self.optimizer.run_adb(f"-s {self.device_id} shell settings put global animator_duration_scale 0.85", timeout=10)
        
        self.root.after(0, self.update_progress, 50, "Limitando Procesos de Fondo y Activando Freezer")
        self.optimizer.run_adb(f"-s {self.device_id} shell settings put global cached_apps_freezer enabled 1", timeout=10)
        
        self.root.after(0, self.update_progress, 80, "Optimizando Bases de Datos (SQLite Vacuum)")
        self.optimizer.run_adb(f"-s {self.device_id} shell cmd package bg-dexopt-job", timeout=40)
        
        self.root.after(0, self.update_progress, 100, "Modo Doze Aplicado")
        self.optimizer.run_adb(f"-s {self.device_id} shell dumpsys deviceidle force-idle", timeout=10)
        
        self.log("--- OPTIMIZACIÓN COMPLETADA ---")
        self.root.after(0, lambda: messagebox.showinfo("Optimización Completa", "El sistema ha sido optimizado con éxito a nivel de Kernel y BD."))
        self.root.after(0, lambda: self.toggle_buttons(False))
        self.root.after(2000, lambda: self.update_progress(0, "Listo"))

    def execute_debloat(self):
        if not self.device_id: return messagebox.showerror("Error", "No hay teléfono conectado.")
        if self.is_processing: return messagebox.showwarning("Espera", "Ya hay un proceso ejecutándose.")
        selected = [pkg for pkg, var in self.check_vars.items() if var.get()]
        if not selected: return messagebox.showwarning("Atención", "No hay aplicaciones marcadas.")
        
        win = tk.Toplevel(self.root)
        win.title("Confirmar Desinstalación")
        win.geometry("400x160")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        
        tk.Label(win, text=f"¿Desea PROCESAR las {len(selected)} apps seleccionadas?", font=("Arial", 10, "bold")).pack(pady=10)
        
        chk_var = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(win, text="Crear copia de seguridad (Sálvame mi app)", variable=chk_var, font=("Arial", 8))
        chk.pack(pady=5)
        
        def proceed():
            make_backup = chk_var.get()
            win.destroy()
            self.toggle_buttons(True)
            threading.Thread(target=self._run_debloat_worker, args=(selected, make_backup), daemon=True).start()
            
        def cancel():
            win.destroy()
            
        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="✅ Proceder", bg="#dc3545", fg="white", font=("Arial", 9, "bold"), width=12, command=proceed).pack(side="left", padx=10)
        tk.Button(btn_frame, text="❌ Cancelar", bg="#6c757d", fg="white", font=("Arial", 9, "bold"), width=12, command=cancel).pack(side="right", padx=10)

    def delete_custom_pkg(self):
        pkg = self.custom_pkg_var.get().strip()
        if not pkg: return messagebox.showwarning("Atención", "Escribe el nombre del paquete (ej. com.ejemplo.app)")
        if not self.device_id: return messagebox.showerror("Error", "No hay teléfono conectado.")
        if messagebox.askyesno("Confirmar", f"¿Seguro de eliminar '{pkg}'?"):
            self.toggle_buttons(True)
            try:
                self.btn_custom_delete.config(state="disabled")
            except:
                pass
            threading.Thread(target=self._run_debloat_worker, args=([pkg], False), daemon=True).start()

    def _run_debloat_worker(self, selected, make_backup):
        self.log(f"--- INICIANDO DESINSTALACIÓN DE {len(selected)} APPS ---")
        _, _, free_antes = self.optimizer.get_storage_stats(self.device_id)
        
        if make_backup and self.device_serial:
            dev_backup_dir = os.path.join(self.backup_dir, self.device_serial)
            os.makedirs(dev_backup_dir, exist_ok=True)
            backup_data = {}
            json_path = os.path.join(dev_backup_dir, "backup.json")
            
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r") as f: backup_data = json.load(f)
                except: pass
            
            total_sel = max(1, len(selected))
            for i, pkg in enumerate(selected):
                self.root.after(0, self.update_progress, int((i/total_sel)*50), f"Respaldando: {pkg}")
                path_out = self.run_adb(f"-s {self.device_id} shell pm path {pkg}", timeout=15)
                
                if "package:" in path_out:
                    apk_remote = path_out.replace("package:", "").strip()
                    apk_local = os.path.join(dev_backup_dir, f"{pkg}.apk")
                    self.run_adb(f'-s {self.device_id} pull {apk_remote} "{apk_local}"', timeout=30)
                    backup_data[pkg] = {"action": "uninstalled", "apk": apk_local}
                    self.log(f"APK Respaldado: {pkg}")
                else:
                    backup_data[pkg] = {"action": "disabled"}
                    self.log(f"Respaldo lógico (Sin APK): {pkg}")
                    
            try:
                with open(json_path, "w") as f:
                    json.dump(backup_data, f, indent=4)
                self.log("Archivo backup.json actualizado exitosamente.")
            except:
                pass

        self.root.after(0, self.update_progress, 60, "Borrando aplicaciones...")
        
        exitosas = []
        fallidas = []
        
        total_sel = max(1, len(selected))
        for i, pkg in enumerate(selected):
            human_name = self.pkg_to_name.get(pkg, pkg)
            self.root.after(0, self.update_progress, 60 + int((i/total_sel)*35), f"Procesando: {human_name}")
            
            res = self.run_adb(f'-s {self.device_id} shell "pm uninstall --user 0 {pkg} || pm disable-user --user 0 {pkg}"', timeout=20)
            
            check_rem = self.run_adb(f'-s {self.device_id} shell pm path {pkg}', timeout=10)
            if "package:" not in check_rem or "Failure" in res:
                state_out = self.run_adb(f'-s {self.device_id} shell pm list packages -d', timeout=10)
                if pkg in state_out:
                    exitosas.append(f"☑ {human_name} (Deshabilitada)")
                    self.log(f"Deshabilitada: {pkg}")
                else:
                    exitosas.append(f"✅ {human_name} (Desinstalada)")
                    self.log(f"Desinstalada: {pkg}")
            else:
                fallidas.append(f"❌ {human_name} [{pkg}]")
                self.log(f"Fallo al procesar: {pkg} -> {res}")

        _, _, free_despues = self.optimizer.get_storage_stats(self.device_id)
        ganancia_mb = max(0, free_despues - free_antes)
        ganancia_gb = round(ganancia_mb / 1024, 2)
        
        self.root.after(0, self.update_progress, 100, "Proceso Finalizado")
        self.log(f"--- DESINSTALACIÓN FINALIZADA (Liberados: {ganancia_gb} GB) ---")
        
        self.root.after(0, lambda: self.custom_pkg_var.set(""))
        self.root.after(0, self.scan_installed_apps_thread)
        self.root.after(0, self.detect_device)
        
        def mostrar_reporte_final():
            rep_win = tk.Toplevel(self.root)
            rep_win.title("CleanPhone Pro - Reporte de Desinstalación")
            rep_win.geometry("500x450")
            rep_win.transient(self.root)
            rep_win.grab_set()
            
            tk.Label(rep_win, text="📋 REPORTE DE PROCESO COMPLETADO", font=("Arial", 11, "bold"), fg="darkblue").pack(pady=10)
            tk.Label(rep_win, text=f"Espacio total liberado: {ganancia_gb} GB", font=("Arial", 10, "bold"), fg="#28a745").pack(pady=2)
            
            txt_frame = tk.Frame(rep_win)
            txt_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            txt_box = tk.Text(txt_frame, bg="#f8f9fa", font=("Consolas", 9))
            scroll = ttk.Scrollbar(txt_frame, orient="vertical", command=txt_box.yview)
            txt_box.configure(yscrollcommand=scroll.set)
            
            txt_box.pack(side="left", fill="both", expand=True)
            scroll.pack(side="right", fill="y")
            
            reporte_texto = f"=== RESUMEN GENERAL ===\n" \
                            f"Total procesadas: {len(selected)}\n" \
                            f"Exitosas: {len(exitosas)}\n" \
                            f"Fallidas / Omitidas: {len(fallidas)}\n\n" \
                            f"--- APPS EXITOSAS ({len(exitosas)}) ---\n" + "\n".join(exitosas) + "\n\n" \
                            f"--- APPS FALLIDAS / PROTEGIDAS ({len(fallidas)}) ---\n" + ("\n".join(fallidas) if fallidas else "Ninguna (Todas OK)")
            
            txt_box.insert(tk.END, reporte_texto)
            txt_box.config(state="disabled")
            
            tk.Button(rep_win, text="Cerrar", bg="#007bff", fg="white", font=("Arial", 9, "bold"), width=15, command=rep_win.destroy).pack(pady=10)

        self.root.after(0, mostrar_reporte_final)
        self.root.after(0, lambda: self.toggle_buttons(False))
        self.root.after(2000, lambda: self.update_progress(0, "Listo"))


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = CleanPhoneApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error Crítico de Ejecución", f"La aplicación se cerró debido a:\n{e}")
