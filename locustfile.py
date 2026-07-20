from locust import HttpUser, task, between
import time

class StudentTestUser(HttpUser):
    # Waktu jeda (delay) antara request dari masing-masing user (1-5 detik)
    wait_time = between(15, 45) 
    
    def on_start(self):
        """
        Dijalankan setiap kali seorang user baru (Virtual User) dibuat.
        User akan login terlebih dahulu untuk mendapatkan JWT Token.
        """
        # TODO: Ganti dengan NIP/NIM dan Password yang ada di database Anda.
        # Jika ingin mengetes untuk banyak user sekaligus, Anda bisa membaca 
        # daftar user dari file CSV lalu mengambilnya secara bergiliran.
        login_payload = {
            "nis_or_nip": "221524044", 
            "password": "Mah044!!"
        }
        
        response = self.client.post("/login", json=login_payload)
        if response.status_code == 200:
            data = response.json()
            # Asumsi response login mengembalikan struktur: {"data": {"token": "ey..."}}
            # Sesuaikan dengan struktur response dari API login Anda
            self.token = data.get("data", {}).get("token", "")
            
            self.headers = {
                "Authorization": f"Bearer {self.token}"
            }
        else:
            self.headers = {}
            print(f"Login failed: {response.text}")

    @task
    def run_test_execution(self):
        """
        Task ini mensimulasikan user menekan tombol "Run Test".
        Locust akan menjalankan task ini berulang kali.
        """
        # Pastikan kita sudah dapat token dari login
        if not self.headers:
            return
            
        # TODO: Ganti 'id_topik_modul' dengan ID valid dari database
        id_topik_modul = "8791f964-a690-490d-83f6-c7ae3ffbccd6"
        
        start_time = time.time() # Mulai catat waktu keseluruhan
        
        response = self.client.post(
            f"/modul/run/{id_topik_modul}",
            headers=self.headers
        )
        
        if response.status_code != 200:
            print(f"Test Execution Failed: {response.status_code} - {response.text}")
            return
            
        task_data = response.json()
        task_id = task_data.get("task_id")
        
        if not task_id:
            print("Failed to get task_id from response")
            return
            
        # Polling status dari task_queue
        while True:
            time.sleep(3) # Jeda 3 detik
            
            status_resp = self.client.get(
                f"/modul/run/status/{task_id}",
                headers=self.headers,
                name="/modul/run/status/[task_id]" # Supaya di log digabung jadi satu endpoint
            )
            
            if status_resp.status_code != 200:
                print(f"Polling Failed: {status_resp.status_code}")
                # Hentikan loop dan catat kegagalan keseluruhan
                total_time_ms = int((time.time() - start_time) * 1000)
                self.environment.events.request.fire(
                    request_type="ASYNC",
                    name="Full Execution (POST + Polling)",
                    response_time=total_time_ms,
                    response_length=0,
                    exception=Exception(f"Polling Failed: {status_resp.status_code}")
                )
                break
                
            status_data = status_resp.json()
            if status_data.get("status") == "completed":
                # Eksekusi selesai dengan sukses
                total_time_ms = int((time.time() - start_time) * 1000)
                # Catat hasil waktu keseluruhan ke Locust UI
                self.environment.events.request.fire(
                    request_type="ASYNC",
                    name="Full Execution (POST + Polling)",
                    response_time=total_time_ms,
                    response_length=0,
                    exception=None
                )
                break
            elif status_data.get("status") == "failed":
                print(f"Execution Failed in Queue: {status_data.get('error')}")
                total_time_ms = int((time.time() - start_time) * 1000)
                self.environment.events.request.fire(
                    request_type="ASYNC",
                    name="Full Execution (POST + Polling)",
                    response_time=total_time_ms,
                    response_length=0,
                    exception=Exception(status_data.get('error'))
                )
                break
