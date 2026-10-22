# SafeTravel - AWS WAS

## 프로젝트 개요
기존 SafeTravel 프로젝트를 AWS 환경에 구성한 WAS 서버 코드입니다.

## 디렉터리
- application/: Python Flask 애플리케이션
- terraform/: AWS WAS 인프라 Terraform 설정

## 주요 기능
- 회원가입, 로그인, 로그아웃
- 회원 탈퇴 및 비밀번호 검증
- MariaDB RDS 연동
- /health 상태 확인
- SOC 보안 이벤트 전송
- WAS Main / Backup 구성
- VPC Peering 네트워크 설정

## 보안 및 운영
- DB 비밀번호와 SOC 토큰은 서버 환경변수로 관리합니다.
- Terraform 상태 파일과 실제 tfvars 파일은 Git에 포함하지 않습니다.
- Terraform 실행 전 필요한 변수와 AWS 자격 증명을 별도로 설정해야 합니다.
- 비밀번호 재설정 기능은 현재 비활성화 상태입니다.

## 참고
이 폴더는 기존 온프레미스 WAS 코드와 별도로 관리하는 AWS 버전입니다.
