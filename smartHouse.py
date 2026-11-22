from abc import ABC, abstractmethod

from exceptions import (
    IDPerangkatTidakValidError,
    NilaiParameterTidakValidError,
    PerangkatDuplikatError,
)


class PerangkatPintar(ABC):
    total_perangkat = 0

    def __init__(self, id_p: str, nama: str):
        if not PerangkatPintar.validasi_id(id_p):
            raise IDPerangkatTidakValidError(
                f"ID perangkat {id_p!r} tidak valid (wajib string, minimal 2 karakter)"
            )
        self._id_perangkat = id_p
        self._nama = nama
        self._aktif = False
        # Subclass memvalidasi parameternya sebelum memanggil super().__init__(),
        # sehingga hanya objek yang lolos semua validasi yang ikut terhitung.
        PerangkatPintar.total_perangkat += 1

    @property
    def id_perangkat(self) -> str:
        return self._id_perangkat

    @property
    def aktif(self) -> bool:
        return self._aktif

    def nyalakan(self) -> None:
        self._aktif = True

    def matikan(self) -> None:
        self._aktif = False

    def status_dasar(self) -> str:
        status = "ON" if self._aktif else "OFF"
        return f"[{self._id_perangkat}] {self._nama} ({status})"

    @abstractmethod
    def info(self) -> str:
        pass

    def __str__(self) -> str:
        return self.info()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PerangkatPintar):
            return self._id_perangkat == other._id_perangkat
        return False

    def __hash__(self) -> int:
        return hash(self._id_perangkat)

    @staticmethod
    def validasi_id(kode: str) -> bool:
        return isinstance(kode, str) and len(kode) >= 2


class TimerMixin:
    def atur_timer(self, jam: str) -> None:
        self._jadwal = jam


def _validasi_rentang(nama: str, val, minimum: int, maksimum: int, satuan: str) -> None:
    # bool adalah subclass int di Python, jadi ditolak secara eksplisit.
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise NilaiParameterTidakValidError(f"{nama} {val!r} bukan angka")
    if not minimum <= val <= maksimum:
        raise NilaiParameterTidakValidError(
            f"{nama} {val}{satuan} ditolak (wajib {minimum}-{maksimum}{satuan})"
        )


class LampuPintar(PerangkatPintar):
    def __init__(self, id_p: str, nama: str, kecerahan: int):
        self.kecerahan = kecerahan
        super().__init__(id_p, nama)

    @property
    def kecerahan(self) -> int:
        return self.__kecerahan

    @kecerahan.setter
    def kecerahan(self, val: int) -> None:
        _validasi_rentang("Kecerahan", val, 0, 100, "%")
        self.__kecerahan = val

    def info(self) -> str:
        return f"{self.status_dasar()} | Kecerahan: {self.__kecerahan}%"

    @classmethod
    def lampu_tidur(cls, id_p: str, nama: str):
        return cls(id_p, nama, 20)


class ACPintar(PerangkatPintar):
    def __init__(self, id_p: str, nama: str, suhu: int):
        self.suhu = suhu
        super().__init__(id_p, nama)

    @property
    def suhu(self) -> int:
        return self.__suhu

    @suhu.setter
    def suhu(self, val: int) -> None:
        _validasi_rentang("Suhu", val, 16, 30, "C")
        self.__suhu = val

    def info(self) -> str:
        return f"{self.status_dasar()} | Suhu: {self.__suhu}C"


class CCTVPintar(PerangkatPintar, TimerMixin):
    def __init__(self, id_p: str, nama: str, jadwal: str):
        super().__init__(id_p, nama)
        self.atur_timer(jadwal)
        self.__merekam = False

    def mulai_rekam(self) -> None:
        self.nyalakan()
        self.__merekam = True

    def henti_rekam(self) -> None:
        self.__merekam = False

    def info(self) -> str:
        rekam = "Merekam" if self.__merekam else "Siaga"
        return f"{self.status_dasar()} | {rekam} | Timer: {self._jadwal}"


class Ruangan:
    def __init__(self, nama_ruangan: str):
        self.__nama_ruangan = nama_ruangan
        self.__perangkat_list = []

    @property
    def nama_ruangan(self) -> str:
        return self.__nama_ruangan

    def tambah_perangkat(self, p: PerangkatPintar) -> None:
        # Operator `in` memakai __eq__, sehingga duplikat dikenali dari ID perangkat.
        if p in self.__perangkat_list:
            raise PerangkatDuplikatError(
                f"Perangkat dengan ID '{p.id_perangkat}' sudah terpasang "
                f"di ruangan '{self.__nama_ruangan}'"
            )
        self.__perangkat_list.append(p)

    def info_ruangan(self) -> str:
        teks = f"=== Ruangan: {self.__nama_ruangan} ==="
        for p in self.__perangkat_list:
            teks += f"\n- {p.info()}"
        return teks


class SmartHub:
    def __init__(self, nama_hub: str):
        self.__nama_hub = nama_hub
        self.__ruangan_list = []
        self.__log_list = []

    def buat_ruangan(self, nama: str) -> Ruangan:
        ruang_baru = Ruangan(nama)
        self.__ruangan_list.append(ruang_baru)
        self.catat_log(f"Ruangan '{nama}' dibuat di {self.__nama_hub}")
        return ruang_baru

    def kontrol_perangkat(self, p: PerangkatPintar, nyala: bool) -> None:
        if nyala:
            p.nyalakan()
            aksi = "dinyalakan"
        else:
            p.matikan()
            aksi = "dimatikan"
        self.catat_log(f"{p} -> {aksi}")

    def catat_log(self, pesan: str) -> None:
        self.__log_list.append(f"[LOG] {pesan}")

    def lihat_log(self) -> None:
        print(f"=== Log {self.__nama_hub} ===")
        for log in self.__log_list:
            print(log)


if __name__ == "__main__":
    hub = SmartHub("Hub Utama")
    r_tamu = hub.buat_ruangan("Ruang Tamu")

    lampu1 = LampuPintar.lampu_tidur("L01", "Lampu Sudut")
    ac1 = ACPintar("AC1", "AC Ruang Tamu", 22)
    cctv1 = CCTVPintar("C01", "CCTV Depan", "22:00")

    r_tamu.tambah_perangkat(lampu1)
    r_tamu.tambah_perangkat(ac1)
    r_tamu.tambah_perangkat(cctv1)

    hub.kontrol_perangkat(lampu1, True)
    hub.kontrol_perangkat(ac1, True)
    cctv1.mulai_rekam()

    print(r_tamu.info_ruangan())
    print(f"Total Perangkat: {PerangkatPintar.total_perangkat}")

    print("\n=== Pengujian Exception Handling ===")

    # Aturan 1: ID perangkat tidak valid.
    try:
        LampuPintar("X", "Lampu Rusak", 50)
    except IDPerangkatTidakValidError as e:
        print(f"[ID] {e}")
        hub.catat_log(f"Gagal membuat perangkat: {e}")

    # Aturan 2: kecerahan di luar rentang; nilai lama tetap dipertahankan.
    try:
        lampu1.kecerahan = 150
    except NilaiParameterTidakValidError as e:
        print(f"[Parameter] {e} -> kecerahan tetap {lampu1.kecerahan}%")
        hub.catat_log(f"Ubah kecerahan ditolak: {e}")

    # Aturan 3: suhu di luar rentang; else hanya jalan jika tidak ada exception.
    try:
        ac1.suhu = 10
    except NilaiParameterTidakValidError as e:
        print(f"[Parameter] {e} -> suhu tetap {ac1.suhu}C")
        hub.catat_log(f"Ubah suhu ditolak: {e}")
    else:
        hub.catat_log(f"Suhu {ac1} diubah")

    # Aturan 4: perangkat duplikat dalam satu ruangan.
    try:
        lampu_duplikat = LampuPintar("L01", "Lampu Cadangan", 80)
        r_tamu.tambah_perangkat(lampu_duplikat)
    except PerangkatDuplikatError as e:
        print(f"[Duplikat] {e}")
        hub.catat_log(f"Tambah perangkat ditolak: {e}")

    print(f"\n{r_tamu.info_ruangan()}")
    # lampu_duplikat valid sebagai objek (hanya ditolak oleh ruangan), jadi ikut terhitung.
    print(f"Total Perangkat: {PerangkatPintar.total_perangkat}\n")
    hub.lihat_log()