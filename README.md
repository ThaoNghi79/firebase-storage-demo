# Firebase Storage Demo: phân quyền theo domain email

Demo cho seminar **Service-Oriented Architecture**: Firebase Storage (File storage, Download URLs, Security Rules).

- Thành viên: Thảo Nghi (524H0019), Như Quỳnh (524H0027)

Demo chạy hoàn toàn trên máy bằng **Firebase Local Emulator Suite** (Auth + Storage). Không cần tạo project trên Firebase Console, không cần đăng nhập Google, không cần thẻ thanh toán.

---

## Mục lục

1. [Tổng quan](#1-tổng-quan)
2. [Cấu trúc thư mục](#2-cấu-trúc-thư-mục)
3. [Cài môi trường](#3-cài-môi-trường)
4. [Chạy Emulator và tạo tài khoản test](#4-chạy-emulator-và-tạo-tài-khoản-test)
5. [Test bằng Backend FastAPI (Integration)](#5-test-bằng-backend-fastapi-integration)
6. [Test bằng trang web demo.html](#6-test-bằng-trang-web-demohtml)
7. [Kết quả mong đợi](#7-kết-quả-mong-đợi)
8. [Lỗi thường gặp](#8-lỗi-thường-gặp)
9. [Giới hạn của demo và khi lên production](#9-giới-hạn-của-demo-và-khi-lên-production)

---

## 1. Tổng quan

### Vì sao dùng Emulator thay vì Firebase thật

Từ ngày 3/2/2026, Cloud Storage for Firebase bắt buộc nâng cấp gói **Blaze** (phải liên kết thẻ ghi nợ hoặc thẻ tín dụng quốc tế), kể cả khi chỉ dùng trong mức miễn phí. Vì vậy demo dùng **Firebase Local Emulator Suite**: bộ giả lập chạy ngay trên máy, có đủ chức năng Auth và Storage, không cần billing, không mất phí.

> **Lưu ý:** dữ liệu trong Emulator chỉ tồn tại khi Emulator đang chạy. Tắt Emulator (Ctrl+C) là mất hết tài khoản và file test, mỗi lần khởi động lại phải tạo tài khoản và upload lại.

### Phân quyền trong demo

Quyền được quyết định bởi `storage.rules`, dựa trên email trong token đăng nhập:

| Email | Upload | Download |
|---|:---:|:---:|
| `@student.tdtu.edu.vn` (Student) | ✅ | ✅ |
| `@tdtu.edu.vn` (Teacher) | ❌ | ✅ |
| Domain khác, ví dụ `@gmail.com` (Outsider) | ❌ | ❌ |

### Luồng hoạt động

1. Người dùng đăng nhập bằng email + mật khẩu qua **Auth Emulator** (cổng 9099) và nhận về **ID token (JWT)** chứa email.
2. Request upload/download gửi tới **Storage Emulator** (cổng 9199) kèm ID token.
3. Storage đối chiếu token với `storage.rules` rồi cho phép (200) hoặc từ chối (403).

Có 2 cách chạy thử:
- **FastAPI** (mục 5): backend đăng nhập thay theo `role`, rồi chuyển tiếp token sang Storage.
- **demo.html** (mục 6): trình duyệt dùng Firebase SDK gọi thẳng Emulator, người dùng tự đăng nhập.

---

## 2. Cấu trúc thư mục

```
.
├── firebase.json      # Cấu hình Emulator (Auth 9099, Storage 9199, UI 4000) và file rules
├── storage.rules      # Security Rules phân quyền theo domain email
├── main.py            # Backend FastAPI: PUT /files, GET /files/{filename}, GET /files/{filename}/url
├── requirements.txt   # Thư viện Python cho backend
├── demo.html          # Trang web demo dùng Firebase SDK
└── README.md
```

Tải code về máy bằng một trong hai cách:
- Bấm nút **Code → Download ZIP** trên GitHub rồi giải nén, hoặc
- Dùng Git: `git clone <link-repo-này>`

---

## 3. Cài môi trường

Bỏ qua bước nào máy đã có.

### a) Node.js

1. Vào https://nodejs.org/en → **Get Node.js** → **Windows Installer**.
2. Mở file `.msi` vừa tải → Next → Next → Install.
3. Restart máy (hoặc ít nhất mở lại Terminal) để PATH được cập nhật.
4. Kiểm tra trong Command Prompt / PowerShell:
   ```
   node -v
   npm -v
   ```
   Hiện số phiên bản là thành công.

### b) Java (bản 21 trở lên)

Firebase Emulator cần Java 21 trở lên.

1. Vào https://www.oracle.com/java/technologies/downloads/ và tải Java 21 hoặc 25.
2. Cài như bình thường.
3. Kiểm tra:
   ```
   java -version
   ```
4. **Nếu chưa có biến môi trường:** Search → gõ "Environment Variables" → *Edit the system environment variables* → *Environment Variables...* → mục *System variables* → chọn **Path** → Edit → New → dán đường dẫn thư mục `\bin` của Java (ví dụ `C:\Program Files\Java\jdk-21\bin`) → **Move Up** lên đầu → OK hết các cửa sổ.
5. **Nếu biến môi trường đang trỏ tới Java bản cũ:** làm như bước 4, rồi xóa dòng Path của bản cũ → OK.
6. Mở Terminal mới, kiểm tra:
   ```
   javac -version
   ```

### c) Python (bản 3.10 trở lên)

Chỉ cần nếu test bằng FastAPI (mục 5).

1. Vào https://www.python.org/downloads/ và tải Python 3.10 trở lên.
2. Mở file cài, **tick ô "Add python.exe to PATH"** ở màn hình đầu tiên → Install Now.
3. Mở Terminal mới, kiểm tra:
   ```
   python --version
   ```

### d) Firebase CLI

Mở Command Prompt hoặc Terminal trong VS Code:
```
npm install -g firebase-tools
```
Kiểm tra:
```
firebase --version
```

---

## 4. Chạy Emulator và tạo tài khoản test

### Bước 1: Khởi động Emulator

Mở thư mục code bằng VS Code (File → Open Folder), mở Terminal và chạy:

```
firebase emulators:start
```

- Lần đầu chạy, CLI sẽ tự tải emulator về nên cần có mạng.
- Thấy dòng `✔ All emulators ready! It is now safe to connect your app.` là thành công.
- Mở http://127.0.0.1:4000/ để xem giao diện quản lý Emulator (Auth / Storage).
- **Giữ nguyên Terminal này** trong suốt quá trình test.

### Bước 2: Tạo 3 tài khoản test (bắt buộc mỗi lần khởi động lại Emulator)

Vào http://127.0.0.1:4000/ → **Authentication** → **Add user**, tạo 3 tài khoản:

| Vai trò | Tên hiển thị (tùy ý) | Email | Mật khẩu |
|---|---|---|---|
| Sinh viên | SV1 | `sv1@student.tdtu.edu.vn` | `123456` |
| Giảng viên | GV1 | `gv1@tdtu.edu.vn` | `123456` |
| Người ngoài | Test | `test@gmail.com` | `123456` |

### Thứ tự test

1. Upload file bằng tài khoản **Student** trước.
2. Sau đó test download bằng **Teacher**.
3. Nếu vừa restart Emulator thì phải tạo lại tài khoản và upload lại trước khi test download.

---

## 5. Test bằng Backend FastAPI (Integration)

Phải đảm bảo Terminal chạy `firebase emulators:start` vẫn đang mở.

### Bước 1: Tạo môi trường ảo và cài thư viện

Trong VS Code, mở **Terminal mới** (giữ nguyên Terminal đang chạy Emulator), gõ lần lượt:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Kích hoạt thành công thì đầu dòng lệnh có chữ `(venv)`.

> **Lỗi thường gặp:** chạy `venv\Scripts\activate` báo lỗi đỏ có dòng *"running scripts is disabled on this system"* (Windows chặn chạy script trong PowerShell).
>
> **Cách sửa:** trong cùng Terminal đó, gõ:
> ```
> Set-ExecutionPolicy -Scope Process RemoteSigned
> ```
> Nếu hỏi xác nhận thì gõ `Y` → Enter, rồi chạy lại `venv\Scripts\activate`. Lệnh này chỉ có tác dụng trong Terminal đang mở, đóng Terminal là hết.

### Bước 2: Chạy backend

```
uvicorn main:app --reload
```

Thấy dòng `Uvicorn running on http://127.0.0.1:8000` là backend đã chạy. Mở http://127.0.0.1:8000/docs để vào **Swagger UI**.

### Bước 3: Thao tác trên Swagger UI

Có 3 role được cấu hình sẵn trong `main.py`: `student`, `teacher`, `outsider`.

| Endpoint | Cách làm | Kết quả |
|---|---|---|
| `PUT /files` | Try it out → nhập `role` → chọn file từ máy → Execute | Upload file vào `files/` |
| `GET /files/{filename}` | Try it out → nhập `role` → nhập tên file đã upload → Execute → bấm **Download file** | Tải nội dung file |
| `GET /files/{filename}/url` | Try it out → nhập `role` → nhập tên file đã upload → Execute | JSON chứa `download_url` (link tải kèm token) |

> Nên dùng file tên không dấu, không ký tự đặc biệt, ví dụ `HelloWorld.java`.

**Cách backend hoạt động:** backend tra bảng `ACCOUNTS` theo `role`, tự đăng nhập vào Auth Emulator để lấy ID token, rồi gửi request sang Storage Emulator kèm header `Authorization: Firebase <idToken>`. Backend không tự quyết định quyền; `storage.rules` quyết định. Truyền `role` qua query chỉ là cách làm tắt cho demo.

---

## 6. Test bằng trang web demo.html

Phải đảm bảo Terminal chạy `firebase emulators:start` vẫn đang mở. Máy cần có mạng vì trang tải thư viện Firebase từ internet.

1. Mở file `demo.html` trực tiếp bằng trình duyệt (double-click).
2. Bấm nút nhanh **"Dùng: Student"** (tự điền email và mật khẩu `123456`) → **Đăng nhập** → chọn file → **Upload**.
3. Đổi sang **"Dùng: Teacher"** → Đăng nhập → thử Upload (phải bị chặn) → thử Tải xuống (phải thành công).
4. Đổi sang **"Dùng: Gmail lạ"** → thử cả upload và tải xuống (phải bị chặn hết).
5. Về chức năng tải file:
   - **Tải xuống**: file tự lưu về máy.
   - **Lấy Download URL**: hiện link có token. Ai có link này cũng tải được, kể cả người chưa đăng nhập.
6. Xem kết quả thực tế: http://127.0.0.1:4000/ → tab **Storage** → chọn bucket `default.appspot.com` → thư mục `files`.

---

## 7. Kết quả mong đợi

| Tài khoản | Upload | Download | Get Download URL |
|---|:---:|:---:|:---:|
| Student | 200 | 200 | 200 |
| Teacher | 403 | 200 | 200 |
| Outsider | 403 | 403 | 403 |

- Trên demo.html, kết quả bị chặn hiện là "Permission Denied" thay cho mã 403.
- 403 ở `/url` nghĩa là không được lấy link mới; các Download URL đã phát trước đó vẫn dùng được cho tới khi token bị thu hồi.

---

## 8. Lỗi thường gặp

| Hiện tượng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `401 Đăng nhập thất bại` (FastAPI) hoặc "Đăng nhập thất bại" (web) | Chưa tạo tài khoản trên Emulator, hoặc vừa restart Emulator | Tạo lại 3 tài khoản ở mục 4 |
| `400 role phải là 1 trong...` | Nhập sai role | Chỉ dùng `student`, `teacher`, `outsider` |
| `404` khi download | File không tồn tại (chưa upload, gõ sai tên, hoặc vừa restart Emulator) | Upload lại bằng Student |
| Web báo "Tải bị chặn" nhưng dòng `Lỗi:` ghi `storage/object-not-found` | File không tồn tại, không phải bị phân quyền chặn | Upload lại bằng Student |
| `firebase` không được nhận là lệnh | Chưa cài Firebase CLI hoặc chưa mở lại Terminal | Làm lại mục 3d, mở Terminal mới |
| Emulator báo lỗi Java | Chưa cài Java hoặc Java dưới bản 21 | Làm lại mục 3b |
| `python` không được nhận là lệnh | Quên tick "Add python.exe to PATH" khi cài | Cài lại Python và tick ô đó |
| Trang demo.html không phản hồi khi bấm | Không có mạng nên không tải được Firebase SDK | Kết nối mạng rồi mở lại trang |

---

## 9. Giới hạn của demo và khi lên production

**Giới hạn của demo:**
- Backend giữ sẵn mật khẩu tài khoản test và nhận `role` qua query chỉ để demo cho nhanh.
- Mọi người dùng chung đường dẫn `files/{fileName}`, nên Student có thể ghi đè hoặc xóa file của Student khác.
- Rules chưa kiểm tra `email_verified`, nên ai cũng có thể tự đăng ký email đuôi `@student.tdtu.edu.vn`.
- Token của Auth Emulator không có chữ ký, chỉ Emulator chấp nhận.
- Tên file có dấu tiếng Việt hoặc ký tự đặc biệt (`#`, `?`) chưa được mã hóa.

**Khi lên production:**
1. Tạo project trên [Firebase Console](https://console.firebase.google.com/), nâng gói Blaze.
2. Bật Authentication (Email/Password) và Storage.
3. Đẩy rules lên: `firebase deploy --only storage`.
4. `demo.html`: thay cấu hình thật (`apiKey`, `projectId`, `storageBucket`) và bỏ 2 dòng `useEmulator`.
5. Backend: client tự đăng nhập và gửi `Authorization: Bearer <idToken>` lên backend, backend chuyển tiếp đúng token đó sang Storage thay vì tự đăng nhập theo `role`.
6. Nên bổ sung: lưu file theo `files/{uid}/{fileName}`, kiểm tra `email_verified`, giới hạn dung lượng và loại file trong rules.
