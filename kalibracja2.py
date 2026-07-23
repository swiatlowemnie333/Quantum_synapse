from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig
import time

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_a6106557ee774c9c9365d47088e2edcf",
        client_secret="7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb"
    )
)
scheduler = SchedulerClient(auth=auth)

# Sprawdz dostepne subcategories
print("=== Sprawdzam dostepne subcategories ===")
try:
    # Proba bez job_subcategory_id
    job1 = scheduler.submit_job(
        JobSubmissionConfig(
            backend_class_id="ionq:forte-1",
            name="Zazul Kalibracja 36q",
            shots=8192,
        ),
        file_path="sonda_36_IONQ.qasm"
    )
    print(f"IonQ Job ID: {job1.id}")
except Exception as e:
    print(f"Blad bez subcategory: {e}")
    print("\nProba z 'public-compute'...")
    try:
        job1 = scheduler.submit_job(
            JobSubmissionConfig(
                backend_class_id="ionq:forte-1",
                job_subcategory_id="public-compute",
                name="Zazul Kalibracja 36q",
                shots=8192,
            ),
            file_path="sonda_36_IONQ.qasm"
        )
        print(f"IonQ Job ID: {job1.id}")
    except Exception as e2:
        print(f"Blad public-compute: {e2}")
        print("\nProba z 'private'...")
        try:
            job1 = scheduler.submit_job(
                JobSubmissionConfig(
                    backend_class_id="ionq:forte-1",
                    job_subcategory_id="private",
                    name="Zazul Kalibracja 36q",
                    shots=8192,
                ),
                file_path="sonda_36_IONQ.qasm"
            )
            print(f"IonQ Job ID: {job1.id}")
        except Exception as e3:
            print(f"Blad private: {e3}")
            print("\nProba z 'standard'...")
            try:
                job1 = scheduler.submit_job(
                    JobSubmissionConfig(
                        backend_class_id="ionq:forte-1",
                        job_subcategory_id="standard",
                        name="Zazul Kalibracja 36q",
                        shots=8192,
                    ),
                    file_path="sonda_36_IONQ.qasm"
                )
                print(f"IonQ Job ID: {job1.id}")
            except Exception as e4:
                print(f"Blad standard: {e4}")
                print("\n❌ WSZYSTKIE PROBY FAILED!")
