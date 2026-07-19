import time
import subprocess

start_time = time.time()

# Define the path to your text file
path_yt = 'yt_links/links.txt'
path_audios = 'yt_links/audio.txt'

# script master to run ALL the steps of the project. 
def main():

    # Open the file and read each line
    with open(path_yt, 'r') as file:
        yt_links = file.readlines()

    # Strip whitespace from each line (e.g., newline characters) and print the links
    yt_links = [youtube_link.strip() for youtube_link in yt_links]

    for youtube_url in yt_links:
        
        print(f'>>> youtube_url: {youtube_url}')

        print('Downloading audio from youtube...')
        subprocess.run(['python3', 'source/extraction.py', youtube_url])

    print("Finished download from youtube.")
    with open(path_audios, 'r') as file:
        audios_links = file.readlines()

    # Strip whitespace from each line (e.g., newline characters) and print the links
    audios_links = [audios_link.strip() for audios_link in audios_links]

    print(audios_links)
    for audio_link in audios_links:
        print(f'>>> audio_link: {audio_link}')

        print('transcripting audio to text file...')
        subprocess.run(['python3', 'source/transcribe_audio.py', audio_link])


if __name__ == "__main__":
    main()