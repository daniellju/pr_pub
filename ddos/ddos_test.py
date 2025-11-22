import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests


def send_request(session, url, timeout):
    """
    Sendet eine einzelne GET-Anfrage und gibt (erfolg, dauer) zurück.
    """
    start = time.time()
    try:
        response = session.get(url, timeout=timeout)
        duration = time.time() - start
        return True, response.status_code, duration
    except requests.RequestException:
        duration = time.time() - start
        return False, None, duration


def main():
    parser = argparse.ArgumentParser(
        description="Einfacher legaler HTTP-Lasttest (begrenzte Anfragen)."
    )
    parser.add_argument(
        "-u", "--url",
        required=True,
        help= "https://resuah.ch"
    )
    parser.add_argument(
        "-n", "--num-requests",
        type=int,
        default=50,
        help="Anzahl der Anfragen (Standard: 50)"
    )
    parser.add_argument(
        "-c", "--concurrency",
        type=int,
        default=5,
        help="Maximale Anzahl gleichzeitiger Anfragen (Standard: 5)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=5.0,
        help="Timeout pro Anfrage in Sekunden (Standard: 5.0)"
    )

    args = parser.parse_args()

    url = args.url
    num_requests = max(1, args.num_requests)
    concurrency = max(1, args.concurrency)
    timeout = args.timeout

    print(f"Starte Lasttest auf: {url}")
    print(f"Anfragen insgesamt : {num_requests}")
    print(f"Gleichzeitige Anfragen (concurrency): {concurrency}")
    print(f"Timeout pro Anfrage: {timeout} s")
    print("-" * 60)

    successes = 0
    failures = 0
    durations = []

    start_total = time.time()

    # Session wiederverwendet TCP-Verbindungen (effizienter, aber noch harmlos)
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [
                executor.submit(send_request, session, url, timeout)
                for _ in range(num_requests)
            ]

            for i, future in enumerate(as_completed(futures), start=1):
                ok, status, duration = future.result()
                durations.append(duration)

                if ok:
                    successes += 1
                    print(f"[{i}/{num_requests}] OK  | Status {status} | {duration:.3f} s")
                else:
                    failures += 1
                    print(f"[{i}/{num_requests}] FAIL|          | {duration:.3f} s")

    total_time = time.time() - start_total

    print("\n=== Zusammenfassung ===")
    print(f"Erfolgreiche Anfragen : {successes}")
    print(f"Fehlgeschlagene      : {failures}")
    print(f"Gesamtdauer          : {total_time:.3f} s")

    if durations:
        avg = sum(durations) / len(durations)
        print(f"Durchschnittliche Antwortzeit: {avg:.3f} s")
        print(f"Schnellste Antwort           : {min(durations):.3f} s")
        print(f"Langsamste Antwort           : {max(durations):.3f} s")

    print("\nHinweis: Bitte nur auf Servern nutzen, für die du eine Test-Erlaubnis hast.")


if __name__ == "__main__":
    main()
