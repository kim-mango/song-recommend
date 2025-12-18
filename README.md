# song-recommend
사용자 음성 분석기반 노래 추천 프로그램
# 실행방법
1. 저음부터 점점 음을 높여 발성 가능한 고음까지 목소리 녹음 하여 scale_up.m4a 생성
2. 자신에게 제일 편안한 톤과 음으로 4~5초 목소리 녹음 하여 sustain_mid.m4a 생성
3. 생성한 녹음 파일 2개를 user_recodings폴더에 넣기(기존파일은 샘플)
4. cmd로 들어가 user_profile.py 실행(성공시, user_profile.json 생성
5. audio폴더에 내가 원하는 곡들 mp3파일로 넣기 - 파일 예시) 제목(가수).mp3
6. cmd로 들어가 build_song_db.py 실행(성공시, songs_profile.csv 생성)
   5~6의 경우 샘플파일이 이미 제공되어 있어 시행하기 싫다면 건너뛰십시오.
7. cmd로 들어가 recommend.py 실행(성공시, cmd에서 추천순으로 10곡 추천)
