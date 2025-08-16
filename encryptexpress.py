#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import os
import subprocess
from urllib.parse import urlparse, unquote

class EncryptExpress(Gtk.Window):
    def __init__(self):
        super(EncryptExpress, self).__init__()
        
        # Resim dosyasının mutlak yolunu dinamik olarak belirle
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(script_dir, "enc.png")
        
        # Translations dictionary
        self.translations = {
            "en": {
                "title": "Encrypt Express",
                "dnd_label": "Drag & Drop a File/Folder Here",
                "source_label": "Select Source:",
                "browse_btn": "Browse",
                "password_label": "Enter Password:",
                "re_password_label": "Re-enter Password:",
                "delete_checkbox": "Permanently shred original file! (recommended)",
                "encrypt_btn": "Encrypt",
                "decrypt_btn": "Decrypt",
                "about_btn": "About",
                "password_error": "Please enter a password!",
                "passwords_not_match": "Passwords do not match, please check!",
                "no_file_selected": "Please select a file or folder to encrypt.",
                "encryption_error": "Encryption error for",
                "encryption_success": "Encryption completed successfully.",
                "decrypt_no_file": "Please select a .7z file to decrypt.",
                "decrypt_only_one": "Please select only one file with .7z extension.",
                "enter_password_title": "Enter Password",
                "file_exists_warning_title": "File Conflict",
                "file_exists_warning_text": "A file/folder with the same name already exists in the target directory. Do you want to overwrite it?",
                "decrypt_cancelled": "Decryption cancelled.",
                "decryption_success": "Decryption completed successfully.",
                "decryption_error": "Decryption error. Password may be wrong or file may be corrupted:",
                "shred_error": "An error occurred during file deletion:",
                "command_not_found": "command not found. Please make sure the package is installed.",
                "about_comments": (
                    "Content encryption application for Debian systems.\n\n"
                    "It secures your files by encrypting them.\n"
                    "If you forget the password, you will lose your files!\n"
                    "This program comes with no warranty."
                ),
                "about_license": "GUI Application: GNU GPLv3\nLicenses: BSD 3, LZMA SDK (Igor Pavlov's 7-zip licences)",
                "about_title": "About Encrypt Express"
            },
            "tr": {
                "title": "Encrypt Express",
                "dnd_label": "Dosyayı/Klasörü buraya sürükle",
                "source_label": "Kaynak Seç:",
                "browse_btn": "Gözat",
                "password_label": "Parola gir:",
                "re_password_label": "Parolayı tekrarla:",
                "delete_checkbox": "Orijinal dosyayı kalıcı yok et! (önerilir)",
                "encrypt_btn": "Şifrele",
                "decrypt_btn": "Şifre Çöz",
                "about_btn": "Hakkında",
                "password_error": "Lütfen parola giriniz!",
                "passwords_not_match": "Parolalar aynı değil, lütfen kontrol edin!",
                "no_file_selected": "Lütfen şifrelemek için bir dosya veya klasör seçin.",
                "encryption_error": "Şifreleme hatası:",
                "encryption_success": "Şifreleme işlemi başarıyla tamamlandı.",
                "decrypt_no_file": "Lütfen şifresini çözmek için bir .7z dosyası seçin.",
                "decrypt_only_one": "Lütfen sadece bir adet .7z uzantılı dosya seçin.",
                "enter_password_title": "Parola Girin",
                "file_exists_warning_title": "Dosya Çakışması",
                "file_exists_warning_text": "Hedef dizinde zaten aynı isimde bir dosya/klasör var. Üzerine yazılsın mı?",
                "decrypt_cancelled": "Şifre çözme işlemi iptal edildi.",
                "decryption_success": "Şifre çözme işlemi başarıyla tamamlandı.",
                "decryption_error": "Şifre çözme hatası. Parola yanlış veya dosya bozuk olabilir:",
                "shred_error": "Dosya silme sırasında bir hata oluştu:",
                "command_not_found": "komutu bulunamadı. Lütfen kurulu olduğundan emin olun.",
                "about_comments": (
                    "Debian sistemler için içerik şifreleme uygulaması.\n\n"
                    "Dosyalarınızı şifreleyerek güvene alır.\n"
                    "Şifreyi unutursanız dosyalarınızı kaybedersiniz!\n"
                    "Bu program hiçbir garanti getirmez."
                ),
                "about_license": "GUI Uygulaması İçin: GNU GPLv3\nLisanslar: BSD 3, LZMA SDK (Igor Pavlov's 7-zip licences)",
                "about_title": "Hakkında"
            }
        }
        self.current_lang = "en"
        
        self.set_default_size(400, 400)
        self.set_border_width(10)
        self.set_resizable(False)

        self.selected_paths = []

        self.css_provider = Gtk.CssProvider()
        css_code = """
            .encrypt-button {
                background-image: none;
                background-color: #e57373; /* Koyu pembe/açık kırmızı */
                border-color: #d32f2f;
                color: #ffffff;
            }
            .decrypt-button {
                background-image: none;
                background-color: #81c784; /* Açık yeşil */
                border-color: #388e3c;
                color: #000000;
            }
        """
        self.css_provider.load_from_data(css_code.encode('utf-8'))
        style_context = self.get_style_context()
        style_context.add_provider_for_screen(self.get_screen(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        try:
            self.set_icon_from_file(self.icon_path)
        except Gtk.Gdk.PixbufError:
            print("Warning: Could not load icon 'enc.png'.")

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_vbox)
        
        top_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        top_hbox.set_halign(Gtk.Align.CENTER)
        
        self.dnd_frame = Gtk.Frame()
        self.dnd_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.dnd_box.set_size_request(250, 100)
        self.dnd_label = Gtk.Label()
        self.dnd_box.pack_start(self.dnd_label, True, True, 0)
        self.dnd_frame.add(self.dnd_box)
        
        try:
            amblem_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.icon_path, 100, 100)
            amblem_image = Gtk.Image.new_from_pixbuf(amblem_pixbuf)
        except Gtk.Gdk.PixbufError:
            amblem_image = Gtk.Label(label="Amblem")
            print("Warning: Could not load amblem image 'enc.png'.")
        
        top_hbox.pack_start(self.dnd_frame, False, False, 0)
        top_hbox.pack_end(amblem_image, False, False, 0)
        
        self.dnd_frame.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.dnd_frame.drag_dest_add_uri_targets()
        self.dnd_frame.connect("drag-data-received", self._on_drag_data_received)

        file_selection_grid = Gtk.Grid()
        file_selection_grid.set_column_spacing(10)
        file_selection_grid.set_row_spacing(10)

        self.target_label = Gtk.Label()
        self.target_label.set_halign(Gtk.Align.START)

        self.target_entry = Gtk.Entry()
        self.target_entry.set_hexpand(True)

        self.browse_btn = Gtk.Button()
        self.browse_btn.set_size_request(80, -1)

        file_selection_grid.attach(self.target_label, 0, 0, 1, 1)
        file_selection_grid.attach(self.target_entry, 1, 0, 1, 1)
        file_selection_grid.attach(self.browse_btn, 2, 0, 1, 1)
        
        self.browse_btn.connect("clicked", self._on_chooser_clicked)

        separator1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

        password_grid = Gtk.Grid()
        password_grid.set_column_spacing(10)
        password_grid.set_row_spacing(10)
        
        self.password_label = Gtk.Label()
        self.password_label.set_halign(Gtk.Align.START)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.password_entry.set_invisible_char("•")
        self.password_entry.set_hexpand(True)
        
        self.re_password_label = Gtk.Label()
        self.re_password_label.set_halign(Gtk.Align.START)

        self.re_password_entry = Gtk.Entry()
        self.re_password_entry.set_visibility(False)
        self.re_password_entry.set_invisible_char("•")
        self.re_password_entry.set_hexpand(True)
        
        password_grid.attach(self.password_label, 0, 0, 1, 1)
        password_grid.attach(self.password_entry, 1, 0, 1, 1)
        password_grid.attach(self.re_password_label, 0, 1, 1, 1)
        password_grid.attach(self.re_password_entry, 1, 1, 1, 1)

        file_selection_grid.set_column_homogeneous(False)
        password_grid.set_column_homogeneous(False)

        self.delete_checkbox = Gtk.CheckButton()

        button_box = Gtk.Box(spacing=10)
        self.encrypt_btn = Gtk.Button()
        self.decrypt_btn = Gtk.Button()
        button_box.pack_start(self.encrypt_btn, True, True, 0)
        button_box.pack_start(self.decrypt_btn, True, True, 0)
        
        self.encrypt_btn.get_style_context().add_class("encrypt-button")
        self.decrypt_btn.get_style_context().add_class("decrypt-button")
        
        self.encrypt_btn.connect("clicked", self._on_encrypt_clicked)
        self.decrypt_btn.connect("clicked", self._on_decrypt_clicked)

        separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

        bottom_hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.language_btn = Gtk.Button(label="Language")
        self.about_btn = Gtk.Button()
        
        self.language_btn.connect("clicked", self._on_language_clicked)
        self.about_btn.connect("clicked", self._on_about_clicked)
        
        bottom_hbox.pack_start(self.language_btn, True, True, 0)
        bottom_hbox.pack_start(self.about_btn, True, True, 0)
        
        main_vbox.pack_start(top_hbox, False, False, 0)
        main_vbox.pack_start(file_selection_grid, False, False, 0) 
        main_vbox.pack_start(separator1, False, False, 0)
        main_vbox.pack_start(password_grid, False, False, 0)
        main_vbox.pack_start(self.delete_checkbox, False, False, 0)
        main_vbox.pack_start(button_box, False, False, 0)
        main_vbox.pack_start(separator2, False, False, 0)
        main_vbox.pack_start(bottom_hbox, False, False, 0)
        
        self._set_language()

    def _set_language(self):
        lang = self.translations[self.current_lang]
        self.set_title(lang["title"])
        self.dnd_label.set_text(lang["dnd_label"])
        self.target_label.set_text(lang["source_label"])
        self.browse_btn.set_label(lang["browse_btn"])
        self.password_label.set_text(lang["password_label"])
        self.re_password_label.set_text(lang["re_password_label"])
        self.delete_checkbox.set_label(lang["delete_checkbox"])
        self.encrypt_btn.set_label(lang["encrypt_btn"])
        self.decrypt_btn.set_label(lang["decrypt_btn"])
        self.about_btn.set_label(lang["about_btn"])

    def _on_language_clicked(self, widget):
        if self.current_lang == "en":
            self.current_lang = "tr"
        else:
            self.current_lang = "en"
        self._set_language()

    def _on_about_clicked(self, widget):
        lang = self.translations[self.current_lang]
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name(lang["title"])
        
        try:
            # Buradaki yol güncellendi.
            about_dialog.set_icon_from_file(self.icon_path)
            about_dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(self.icon_path))
        except Gtk.Gdk.PixbufError:
            print("Uyarı: 'enc.png' simgesi yüklenemedi.")

        about_dialog.set_version("1.0.1")
        about_dialog.set_copyright("Telif Hakkı © 2025 A. Serhat KILIÇOĞLU")
        about_dialog.set_comments(lang["about_comments"])
        about_dialog.set_license(lang["about_license"])
        about_dialog.set_authors(["A. Serhat KILIÇOĞLU"])
        about_dialog.set_translator_credits("Google Gemini AI") 
        about_dialog.set_website("https://www.github.com/shampuan")
        about_dialog.set_title(lang["about_title"])

        about_dialog.run()
        about_dialog.destroy()

    def _on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        uris = data.get_uris()
        file_paths = []
        for uri in uris:
            parsed_uri = urlparse(uri)
            if parsed_uri.scheme == 'file':
                file_path = unquote(parsed_uri.path)
                if os.name == 'nt' and file_path.startswith('/'):
                    file_path = file_path[1:]
                file_paths.append(file_path)
        
        if file_paths:
            self._on_files_selected(file_paths)
            return True
        else:
            return False

    def _on_chooser_clicked(self, widget):
        lang = self.translations[self.current_lang]
        dialog = Gtk.FileChooserDialog(
            title=lang["source_label"],
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, lang["browse_btn"], Gtk.ResponseType.OK)
        )
        dialog.set_select_multiple(True)
        dialog.set_local_only(False)
        dialog.set_current_folder(os.path.expanduser('~'))
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected_paths = dialog.get_filenames()
            self._on_files_selected(selected_paths)
        
        dialog.destroy()

    def _on_files_selected(self, paths):
        lang = self.translations[self.current_lang]
        self.selected_paths = paths
        if paths:
            if len(paths) == 1:
                self.target_entry.set_text(paths[0])
            else:
                self.target_entry.set_text(f"{paths[0]}, and {len(paths) - 1} more file...")
                if self.current_lang == "tr":
                    self.target_entry.set_text(f"{paths[0]}, ve {len(paths) - 1} dosya daha...")
            
            self.dnd_label.set_text(lang["dnd_label"].replace("Drag & Drop a File/Folder Here", "Selection made.").replace("Dosyayı/Klasörü buraya sürükle", "Seçim yapıldı."))
        else:
            self.target_entry.set_text("")
            self.dnd_label.set_text(lang["dnd_label"])

    def _on_encrypt_clicked(self, widget):
        lang = self.translations[self.current_lang]
        password = self.password_entry.get_text()
        re_password = self.re_password_entry.get_text()

        if not password or not re_password:
            self._show_message_dialog("Hata" if self.current_lang == "tr" else "Error", lang["password_error"])
            return

        if password != re_password:
            self._show_message_dialog("Hata" if self.current_lang == "tr" else "Error", lang["passwords_not_match"])
            return

        if not self.selected_paths:
            self._show_message_dialog("Hata" if self.current_lang == "tr" else "Error", lang["no_file_selected"])
            return

        self._encrypt_files(password)

    def _on_decrypt_clicked(self, widget):
        lang = self.translations[self.current_lang]
        if not self.selected_paths:
            self._show_message_dialog("Hata" if self.current_lang == "tr" else "Error", lang["decrypt_no_file"])
            return
        
        if len(self.selected_paths) > 1 or not self.selected_paths[0].endswith('.7z'):
            self._show_message_dialog("Hata" if self.current_lang == "tr" else "Error", lang["decrypt_only_one"])
            return

        self._show_decrypt_password_dialog()

    def _show_decrypt_password_dialog(self):
        lang = self.translations[self.current_lang]
        dialog = Gtk.Dialog(lang["enter_password_title"], self, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        content_area = dialog.get_content_area()
        
        label_password = Gtk.Label(lang["password_label"])
        self.decrypt_password_entry = Gtk.Entry()
        self.decrypt_password_entry.set_visibility(False)
        self.decrypt_password_entry.set_invisible_char("•")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_border_width(10)
        vbox.pack_start(label_password, False, False, 0)
        vbox.pack_start(self.decrypt_password_entry, False, False, 0)
        content_area.pack_start(vbox, True, True, 0)
        
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            password = self.decrypt_password_entry.get_text()
            self._get_dest_directory(password)
        
        dialog.destroy()

    def _get_dest_directory(self, password):
        lang = self.translations[self.current_lang]
        dialog = Gtk.FileChooserDialog(
            title="Hedef Klasör Seç" if self.current_lang == "tr" else "Select Target Folder",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, lang["browse_btn"].replace("Gözat", "Seç").replace("Browse", "Select"), Gtk.ResponseType.OK)
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dest_dir = dialog.get_filename()
            dialog.destroy()
            self._check_and_decrypt(password, dest_dir)
        else:
            dialog.destroy()

    def _check_and_decrypt(self, password, dest_dir):
        lang = self.translations[self.current_lang]
        source_path = self.selected_paths[0]
        base_name = os.path.basename(source_path).removesuffix('.7z')
        target_path = os.path.join(dest_dir, base_name)

        if os.path.exists(target_path):
            dialog = Gtk.MessageDialog(
                self, 
                0, 
                Gtk.MessageType.WARNING, 
                Gtk.ButtonsType.YES_NO, 
                lang["file_exists_warning_title"]
            )
            dialog.format_secondary_text(lang["file_exists_warning_text"])
            response = dialog.run()
            dialog.destroy()
            
            if response != Gtk.ResponseType.YES:
                self._show_message_dialog(lang["decrypt_cancelled"], "")
                return

        self._decrypt_file(password, dest_dir)

    def _decrypt_file(self, password, dest_dir):
        lang = self.translations[self.current_lang]
        source_path = self.selected_paths[0]
        
        command = ['7z', 'x', f'-p{password}', source_path, f'-o{dest_dir}']
        
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"'{source_path}' başarıyla şifresi çözüldü.")

            if self.delete_checkbox.get_active():
                self._shred_file(source_path)

            self._show_message_dialog(lang["decryption_success"], "")

        except subprocess.CalledProcessError as e:
            self._show_message_dialog("Hata" if self.current_lang == "tr" else "Error", f"{lang['decryption_error']}\n{e.stderr}")
        except FileNotFoundError:
            self._show_message_dialog("Hata" if self.current_lang == "tr" else "Error", f"7z {lang['command_not_found']}")

    def _encrypt_files(self, password):
        lang = self.translations[self.current_lang]
        for source_path in self.selected_paths:
            target_path = source_path + ".7z"
            
            command = ['7z', 'a', '-t7z', '-m0=Copy', f'-p{password}', target_path, source_path]
            
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                print(f"'{source_path}' başarıyla şifrelendi.")

                if self.delete_checkbox.get_active():
                    self._shred_file(source_path)

            except subprocess.CalledProcessError as e:
                self._show_message_dialog("Hata" if self.current_lang == "tr" else "Error", f"'{source_path}' {lang['encryption_error']}:\n{e.stderr}")
                return
            except FileNotFoundError:
                self._show_message_dialog("Hata" if self.current_lang == "tr" else "Error", f"7z {lang['command_not_found']}")
                return

        self._show_message_dialog(lang["encryption_success"], "")
        
    def _shred_file(self, file_path):
        lang = self.translations[self.current_lang]
        command = ['shred', '-n', '1', '-u', file_path]
        
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"'{file_path}' başarıyla kalıcı olarak yok edildi.")
        except subprocess.CalledProcessError as e:
            self._show_message_dialog("Hata" if self.current_lang == "tr" else "Error", f"{lang['shred_error']}\n{e.stderr}")
        except FileNotFoundError:
            self._show_message_dialog("Hata" if self.current_lang == "tr" else "Error", f"shred {lang['command_not_found']}")

    def _show_message_dialog(self, title, message):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, title)
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


def main():
    win = EncryptExpress()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
