유진씨 폴더

## DB 구성

- MariaDB GTID 기반 Primary/Replica 복제
- Keepalived를 이용한 DB 장애조치 및 VIP 이동
- NFS를 이용한 DB 자동 백업

## 폴더

- database : DB 및 초기 데이터
- replication : DB1/DB2 MariaDB 복제 설정
- high_availability : Keepalived 및 Failover 스크립트
- backup : NFS 백업 설정 및 스크립트

※ 비밀번호 및 인증정보는 GitHub에 포함하지 않음
