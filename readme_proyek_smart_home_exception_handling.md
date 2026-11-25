# Sistem Smart Home — Pengembangan Exception Handling (Python OOP)

Pengembangan proyek Ujian Tengah Semester (UTS) Pemrograman Berorientasi Objek dengan studi kasus **Sistem Smart Home** melalui penambahan mekanisme *exception handling* (penanganan pengecualian) menggunakan *custom exception*.

## Anggota Kelompok

| No | Nama Lengkap | NIM | Akun GitHub |
| :-: | :--- | :--- | :--- |
| 1 | `[Made Bayu Ardana Putra]` | `[Isi NIM 1]` | `@username1` |
| 2 | `[I Putu Satya Darmika]` | `[Isi NIM 2]` | `@username2` |
| 3 | `[Gusti Gede Agung Rama Putra Udiana]` | `[Isi NIM 3]` | `@username3` |

---

## 1. Identifikasi Aturan Bisnis yang Dapat Dilanggar

Sistem **Smart Home** terdiri atas kelas `SmartHub`, `Ruangan`, `PerangkatPintar` (Abstract Class), `TimerMixin`, `LampuPintar`, `ACPintar`, dan `CCTVPintar`. Berikut adalah lima aturan bisnis yang dapat dilanggar beserta lokasi validasinya pada kelas domain:

| No | Aturan Bisnis | Kondisi Pelanggaran | Kelas & Method Terkait |
| :-: | :--- | :--- | :--- |
| 1 | **Format ID Perangkat Wajib Valid** | ID perangkat bukan bertipe `str` atau panjang karakternya kurang dari 2 karakter. | `PerangkatPintar.__init__()` & `validasi_id()` |
| 2 | **Rentang Kecerahan Lampu (0–100%)** | Nilai kecerahan yang dimasukkan kurang dari `0` atau lebih dari `100`. | `LampuPintar.kecerahan` (`@kecerahan.setter`) |
| 3 | **Rentang Suhu AC (16–30°C)** | Nilai suhu yang dimasukkan kurang dari `16` atau lebih dari `30`. | `ACPintar.suhu` (`@suhu.setter`) |
| 4 | **Tidak Boleh Ada Perangkat Duplikat dalam Satu Ruangan** | Menambahkan objek perangkat yang memiliki `_id_perangkat` sama dengan perangkat yang sudah terdaftar di dalam ruangan tersebut (menggunakan perbandingan `__eq__`). | `Ruangan.tambah_perangkat()` |
| 5 | **Format Jadwal Timer Wajib `HH:MM` (24 Jam)** | Jadwal timer pada perangkat diisi dengan string kosong, format bukan `HH:MM`, atau jam/menit di luar rentang valid (`00:00`–`23:59`). | `TimerMixin.atur_timer()` (diwarisi `CCTVPintar`) |

### Diagram Kelas Sistem

Diagram berikut menunjukkan seluruh kelas domain, atribut, method, serta hubungan antarkelas pada sistem Smart Home. Method bertanda `[!]` merupakan lokasi pelemparan *custom exception*.

```mermaid
classDiagram
    class SmartHub {
        -__nama_hub: str
        -__ruangan_list: list
        -__log_list: list
        +buat_ruangan(nama: str) Ruangan
        +kontrol_perangkat(p: PerangkatPintar, nyala: bool)
        +catat_log(pesan: str)
        +lihat_log()
    }

    class Ruangan {
        -__nama_ruangan: str
        -__perangkat_list: list
        +nama_ruangan() str «property»
        +tambah_perangkat(p: PerangkatPintar) [!]
        +info_ruangan() str
    }

    class PerangkatPintar {
        <<abstract>>
        +total_perangkat: int$
        #_id_perangkat: str
        #_nama: str
        #_aktif: bool
        +__init__(id_p: str, nama: str) [!]
        +id_perangkat() str «property»
        +aktif() bool «property»
        +nyalakan()
        +matikan()
        +status_dasar() str
        +info() str*
        +__eq__(other: object) bool
        +__hash__() int
        +__str__() str
        +validasi_id(kode: str) bool$
    }

    class LampuPintar {
        -__kecerahan: int
        +kecerahan() int «property»
        +kecerahan.setter(val: int) [!]
        +info() str
        +lampu_tidur(id_p: str, nama: str) LampuPintar «classmethod»
    }

    class ACPintar {
        -__suhu: int
        +suhu() int «property»
        +suhu.setter(val: int) [!]
        +info() str
    }

    class CCTVPintar {
        -__merekam: bool
        +mulai_rekam()
        +henti_rekam()
        +info() str
    }

    class TimerMixin {
        <<mixin>>
        #_POLA_JADWAL: Pattern$
        #_jadwal: str
        +atur_timer(jam: str) [!]
    }

    SmartHub *-- Ruangan : komposisi
    Ruangan o-- PerangkatPintar : agregasi
    PerangkatPintar <|-- LampuPintar
    PerangkatPintar <|-- ACPintar
    PerangkatPintar <|-- CCTVPintar
    TimerMixin <|-- CCTVPintar
```

**Keterangan & Cara Membaca Diagram:**
- **Komposisi (`SmartHub *-- Ruangan`)**: `Ruangan` dibuat di dalam `SmartHub` melalui `buat_ruangan()`, sehingga `SmartHub` memiliki `Ruangan` sepenuhnya. Satu hub dapat memiliki banyak ruangan.
- **Agregasi (`Ruangan o-- PerangkatPintar`)**: objek perangkat dibuat di luar lalu dimasukkan ke ruangan melalui `tambah_perangkat()`. Satu ruangan dapat berisi banyak perangkat, dan objek perangkat tetap dapat ada tanpa ruangan.
- **Pewarisan & Multiple Inheritance (`<|--`)**: `LampuPintar`, `ACPintar`, dan `CCTVPintar` mewarisi kelas abstrak `PerangkatPintar`. `CCTVPintar` juga mewarisi `TimerMixin` untuk fitur jadwal timer.
- **Visibilitas & Penanda**: `+` (*public*), `#` (*protected*, `_x`), `-` (*private*, `__x`), garis bawah (*static* / atribut kelas), miring (*abstract*), dan `[!]` (method yang melempar *custom exception*).

---

## 2. Hierarki Custom Exception

Untuk menangani pelanggaran aturan bisnis di atas secara terstruktur, sistem ini mendefinisikan satu *base exception* (`SmartHomeError`) yang mewarisi kelas bawaan `Exception` di Python, beserta empat kelas turunannya.

### Struktur Hierarki

```text
Exception (Python built-in)
└── SmartHomeError                     # Base exception sistem Smart Home
    ├── IDPerangkatTidakValidError     # Pelanggaran format/panjang ID perangkat
    ├── NilaiParameterTidakValidError  # Pelanggaran batas kecerahan lampu & suhu AC
    ├── PerangkatDuplikatError         # Pelanggaran duplikasi ID perangkat di Ruangan
    └── JadwalTimerTidakValidError     # Pelanggaran format waktu pada TimerMixin
```

### Diagram Pewarisan Exception

```mermaid
classDiagram
    class Exception {
        <<built-in>>
    }
    class SmartHomeError {
        <<Base Exception>>
    }
    class IDPerangkatTidakValidError
    class NilaiParameterTidakValidError
    class PerangkatDuplikatError
    class JadwalTimerTidakValidError

    Exception <|-- SmartHomeError
    SmartHomeError <|-- IDPerangkatTidakValidError
    SmartHomeError <|-- NilaiParameterTidakValidError
    SmartHomeError <|-- PerangkatDuplikatError
    SmartHomeError <|-- JadwalTimerTidakValidError
```

### Deskripsi Kelas Exception

1. **`SmartHomeError(Exception)`**  
   *Base exception* untuk seluruh kesalahan domain pada sistem Smart Home. Digunakan sebagai induk agar program utama dapat menangkap pengecualian sistem secara spesifik maupun umum.
2. **`IDPerangkatTidakValidError(SmartHomeError)`**  
   Dilempar ketika `PerangkatPintar` diinstansiasi dengan ID yang tidak memenuhi kriteria `validasi_id()`.
3. **`NilaiParameterTidakValidError(SmartHomeError)`**  
   Dilempar oleh setter `kecerahan` pada `LampuPintar` (di luar rentang 0–100%) atau setter `suhu` pada `ACPintar` (di luar rentang 16–30°C).
4. **`PerangkatDuplikatError(SmartHomeError)`**  
   Dilempar oleh `Ruangan.tambah_perangkat()` ketika perangkat dengan ID yang sama sudah terpasang di dalam daftar perangkat ruangan.
5. **`JadwalTimerTidakValidError(SmartHomeError)`**  
   Dilempar oleh `TimerMixin.atur_timer()` ketika format jadwal tidak sesuai dengan pola waktu 24 jam (`HH:MM`).

### Rancangan Kode (`exceptions.py`)

```python
class SmartHomeError(Exception):
    """Base exception untuk seluruh kesalahan domain pada sistem Smart Home."""
    pass


class IDPerangkatTidakValidError(SmartHomeError):
    """Dilempar ketika ID perangkat bukan string atau panjangnya kurang dari 2 karakter."""
    pass


class NilaiParameterTidakValidError(SmartHomeError):
    """Dilempar ketika nilai parameter perangkat (kecerahan/suhu) di luar rentang valid."""
    pass


class PerangkatDuplikatError(SmartHomeError):
    """Dilempar ketika perangkat dengan ID yang sama sudah terpasang di dalam ruangan."""
    pass


class JadwalTimerTidakValidError(SmartHomeError):
    """Dilempar ketika format jadwal timer tidak sesuai format 24 jam (HH:MM)."""
    pass
```

---

## 3. Implementasi pada Kelas Domain

| Aturan | Sebelum | Sesudah |
| :-: | :--- | :--- |
| 1 | `raise ValueError(...)` | `raise IDPerangkatTidakValidError(...)` |
| 2 & 3 | Setter hanya `print("Error ...")`, nilai salah diabaikan diam-diam | Setter melempar `NilaiParameterTidakValidError` (rentang salah atau bukan angka) |
| 4 | `tambah_perangkat()` langsung `append` | Cek `p in daftar` (memakai `__eq__`) lalu lempar `PerangkatDuplikatError` |
| 5 | `atur_timer()` langsung menyimpan nilai | Validasi regex `HH:MM` 24 jam, lempar `JadwalTimerTidakValidError` |

Perbaikan pendukung:

- Subclass memvalidasi parameternya **sebelum** `super().__init__()`, sehingga `PerangkatPintar.total_perangkat` hanya bertambah untuk objek yang berhasil dibuat.
- Ditambahkan `__hash__` (pasangan `__eq__`) agar perangkat dapat dipakai di `set`/`dict`, serta property `id_perangkat`.
- Pesan error yang tertangkap dicatat ke log `SmartHub` melalui `catat_log()`.

## 4. Struktur File & Cara Menjalankan

```text
SmartHouse/
├── exceptions.py   # Hierarki custom exception
└── smartHouse.py   # Kelas domain + program utama (demo try/except)
```

```bash
python smartHouse.py
```

## 5. Contoh Penanganan di Program Utama

Program utama menguji kelima aturan dengan `try/except`, termasuk blok `else` dan `finally`, serta penangkapan umum lewat base exception `SmartHomeError`:

```python
try:
    r_tamu.tambah_perangkat(LampuPintar("L01", "Lampu Cadangan", 80))
except PerangkatDuplikatError as e:      # tangkap spesifik
    hub.catat_log(f"Tambah perangkat ditolak: {e}")

try:
    CCTVPintar("C02", "CCTV Belakang", "25:00")
except SmartHomeError as e:               # tangkap umum via base exception
    print(f"[{type(e).__name__}] {e}")
finally:
    hub.catat_log("Percobaan jadwal selesai diproses")
```

Cuplikan output:

```text
=== Pengujian Exception Handling ===
[ID] ID perangkat 'X' tidak valid (wajib string, minimal 2 karakter)
[Parameter] Kecerahan 150% ditolak (wajib 0-100%) -> kecerahan tetap 20%
[Parameter] Suhu 10C ditolak (wajib 16-30C) -> suhu tetap 22C
[Duplikat] Perangkat dengan ID 'L01' sudah terpasang di ruangan 'Ruang Tamu'
[JadwalTimerTidakValidError] Jadwal '25:00' tidak valid (wajib format HH:MM, 00:00-23:59)
[JadwalTimerTidakValidError] Jadwal '7:30' tidak valid (wajib format HH:MM, 00:00-23:59)
[JadwalTimerTidakValidError] Jadwal '' tidak valid (wajib format HH:MM, 00:00-23:59)
```
