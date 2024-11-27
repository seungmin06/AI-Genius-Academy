## 🎓 AI 자세교정 의자 "로컬디스크 C"
<img src="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbGvXFZ%2FbtsKOM9wo1H%2F172rBmaE6NHV1I74LeAom1%2Fimg.png" style="width:400px">
<p>LG CNS에서 주최하는 대회인 <b>AI Genius Academy</b>에 참여하여 대상을 받은 프로젝트입니다.</p> 

 
## 🎓 프로젝트 소개
- 압력센서와 인공지능 종아리 인식을 기반으로 하여 자세를 교정, 피드백해주는 자세교정 의자입니다.
  
<img src="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fd8EDgy%2FbtsKN1zxGSO%2F1KAaaUekfW09KGMYhbKJZ0%2Fimg.png" 
 style="width:300px">
- 하판에 12개의 압력센서와 등받이에 4개의 압력센서의 실시간 데이터로 현재 자세를 scikit-learn의 SGD classifier (확률적 경사하강법 선형분류)로 자세를 분류합니다
  
<img src="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fb3Wt3l%2FbtsKN430ES1%2FuDVFjYROlYkaMNBKef8vIk%2Fimg.png" 
 style="width:300px">
- 의자 아래 카메라를 두고 직접 학습시킨 종아리 사진 851개를 YOLO v11-segment 모델을 이용하여 종아리 라벨링 후, 종아리를 11자로 두고 있는지, X자로 두고 있는지 확인합니다.

## 🎓 팀원 소개
|윤승민|김신형|박유노|정찬혁|
|------|---|---|---|
|<a href="https://github.com/seungmin06">seungmin06</a>|<a href="https://github.com/Sunday3960">Sunday3960</a>|<a href="https://github.com/hia1234">hia1234</a>|<a href="https://github.com/Developer-Duck">Developer-Duck</a>|

## 🎓 개발 환경
- RaspBerry pi 5 : 하드웨어 구성 / 카메라 객체인식
- Arduino Mega 2560 : 하드웨어 구성 / 압력센서 (FSR 402)
- Python : <a href="https://huggingface.co/myshell-ai/MeloTTS-Korean">HuggingFace-MeloTTS</a>, GoogleCloud-VertexAi, YOLOv11, SGD classifier, PyQt5
- Daiso

## 개선사항
- 압력센서의 분포도나, 개수가 부족하여 분류하는데 정확도가 낮음 -> 압력센서 추가
