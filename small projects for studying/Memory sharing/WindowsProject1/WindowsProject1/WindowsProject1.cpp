#include <windows.h>
#include <conio.h>
#include <tchar.h>
#pragma comment(lib, "user32.lib")

LRESULT CALLBACK WndProc(HWND, UINT, WPARAM, LPARAM);
DWORD WINAPI ThreadFunc(LPVOID prc);
void DoCreateMain(HWND hWnd);
void DoButtonMain(HWND hWnd);
void DoPaintMain(HWND hWnd);
void OnTimer(HWND hWnd);

#define R 20
#define BOUNCE 1
#define W 20
#define H 100

HBITMAP hBit;
HINSTANCE g_hInst;
HWND hWndMain, hWnd2;
HANDLE hThread;
LPCTSTR lpszClass = TEXT("Bounce1");
RECT crt;
int btnflag = 0;

// Ball
int x, y;
int xv, yv;
int without_ball = 1;

// Stick
int sX[2];
int sY[2];
float sXv[2];
float sYv[2];

void moveStick();
void moveBall();
void collision();

TCHAR shared_memory_location[] = TEXT("Global//shared_space");
HANDLE shared_memory;
class Ball_information {
public:
	int y, xv, yv;
	bool ball_sent_to_1, ball_sent_to_2, ball_sent_to_3;
};
Ball_information* ball_information;

// Threads
DWORD WINAPI ThreadStick(PVOID pArg) {
	Sleep(100);
	while (1) {
		Sleep(30);
		moveStick();
	}
}
DWORD WINAPI ThreadMovingBall(PVOID pArg) {
	Sleep(100);
	while (1) {
		if (without_ball == 0) {
			Sleep(30);
			moveBall();
		}
	}
}
DWORD WINAPI ThreadCollision(PVOID pArg) {
	Sleep(100);
	while (1) {
		if (without_ball == 0) {
			Sleep(30);
			collision();
		}
	}
}
DWORD WINAPI ball_receiver(PVOID pArg) {
	Sleep(100);
	while (1) {
		if (ball_information->ball_sent_to_1) { // When ball information has arrived
			y = ball_information->y;
			xv = ball_information->xv;
			yv = ball_information->yv;
			ball_information->ball_sent_to_1 =false;
			without_ball = 0;
		}
	}
}


int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpszCmdParam, int nCmdShow) {
	HWND hWnd;
	MSG Message;
	WNDCLASS WndClass;
	g_hInst = hInstance;

	WndClass.cbClsExtra = 0;
	WndClass.cbWndExtra = 0;
	WndClass.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
	WndClass.hCursor = LoadCursor(NULL, IDC_ARROW);
	WndClass.hIcon = LoadIcon(NULL, IDI_APPLICATION);
	WndClass.hInstance = hInstance;
	WndClass.lpfnWndProc = (WNDPROC)WndProc;
	WndClass.lpszClassName = lpszClass;
	WndClass.lpszMenuName = NULL;
	WndClass.style = CS_HREDRAW | CS_VREDRAW;
	RegisterClass(&WndClass);

	hWnd = CreateWindow(lpszClass, lpszClass, WS_BORDER | WS_CAPTION | WS_SYSMENU,
		CW_USEDEFAULT, CW_USEDEFAULT, 300, 600,
		NULL, (HMENU)NULL, hInstance, NULL);
	ShowWindow(hWnd, nCmdShow);
	hWndMain = hWnd;

	while (GetMessage(&Message, 0, 0, 0)) {
		TranslateMessage(&Message);
		DispatchMessage(&Message);
	}
	return (int)Message.wParam;
}

LRESULT CALLBACK WndProc(HWND hWnd, UINT iMessage, WPARAM wParam, LPARAM lParam)
{
	COPYDATASTRUCT* pcds;

	switch (iMessage) {

	case WM_CREATE:
		DoCreateMain(hWnd);
		break;
	case WM_PAINT:
		DoPaintMain(hWnd);
		break;
	case WM_LBUTTONDOWN:
		DoButtonMain(hWnd);
		break;
	case WM_TIMER:
		OnTimer(hWnd);
		break;
	case WM_DESTROY:
		PostQuitMessage(0);
		KillTimer(hWnd, 0);
		CloseHandle(hThread);
		return 0;
	}
	return(DefWindowProc(hWnd, iMessage, wParam, lParam));
}

void DoCreateMain(HWND hWnd)
{
	GetClientRect(hWnd, &crt);

	x = 80;	//공의 x 좌표 초기값
	y = 250;//공의 y 좌표 초기값

	xv = (rand() % 4) + 5; //x벡터 속도
	yv = (rand() % 4) + 5; //y벡터 속도


	sX[0] = 0; sY[0] = H; //왼쪽 스틱 초기값
	sYv[0] = 10; //sXv[0] = 50; //왼쪽 스틱 속도

	sX[1] = crt.right - W; sY[1] = H + 50; //오른쪽 스틱 초기값
	sYv[1] = 5; //sXv[1] = 50; //오른쪽 스틱 속도

	// Shared memory configuration
	shared_memory = CreateFileMapping(
		INVALID_HANDLE_VALUE,
		NULL,
		PAGE_READWRITE,
		0,
		sizeof(Ball_information),
		shared_memory_location);

	ball_information = (Ball_information*)MapViewOfFile(shared_memory,
		FILE_MAP_ALL_ACCESS,
		0,
		0,
		sizeof(Ball_information));

	// Create threads
	HANDLE hThreadMovingBall = CreateThread(NULL, 0, ThreadMovingBall, (PVOID)hWndMain, 0, NULL);
	HANDLE hThreadStick = CreateThread(NULL, 0, ThreadStick, (PVOID)hWndMain, 0, NULL);
	HANDLE hThreadCollision = CreateThread(NULL, 0, ThreadCollision, (PVOID)hWndMain, 0, NULL);
	HANDLE h_thread_ball_receiver = CreateThread(NULL, 0, ball_receiver, (PVOID)hWndMain, 0, NULL);
}

void DoPaintMain(HWND hWnd)
{
	HDC hdc, hMemDC;
	PAINTSTRUCT ps;
	HBITMAP OldBit;

	hdc = BeginPaint(hWnd, &ps);

	hMemDC = CreateCompatibleDC(hdc);
	OldBit = (HBITMAP)SelectObject(hMemDC, hBit);
	BitBlt(hdc, 0, 0, crt.right, crt.bottom, hMemDC, 0, 0, SRCCOPY);

	SelectObject(hMemDC, OldBit);
	DeleteDC(hMemDC);
	EndPaint(hWnd, &ps);
	return;
}

void DoButtonMain(HWND hWnd)
{
	if (btnflag == 0) {
		MessageBox(hWnd, TEXT("프로그램이 실행되었습니다."), TEXT("OK"), MB_OK);
		SetTimer(hWnd, 1, 25, NULL);
		btnflag = 1;
	}
	else if (btnflag > 0) {
		x = 250;
		y = 200;
		xv *= -(BOUNCE);
		without_ball = 0;
	}
}

void OnTimer(HWND hWnd)
{
	TCHAR str[123];
	HDC hdc, hMemDC;
	HBITMAP OldBit;
	HPEN hPen, OldPen;
	HBRUSH hBrush, OldBrush;

	hdc = GetDC(hWnd);
	GetClientRect(hWnd, &crt);
	if (hBit == NULL)
	{
		hBit = CreateCompatibleBitmap(hdc, crt.right, crt.bottom);
	}
	hMemDC = CreateCompatibleDC(hdc);
	OldBit = (HBITMAP)SelectObject(hMemDC, hBit);

	FillRect(hMemDC, &crt, GetSysColorBrush(COLOR_WINDOW));

	hPen = CreatePen(PS_INSIDEFRAME, 2, RGB(0, 0, 0));
	OldPen = (HPEN)SelectObject(hMemDC, hPen);
	hBrush = CreateSolidBrush(RGB(255, 120, 0));
	OldBrush = (HBRUSH)SelectObject(hMemDC, hBrush);
	Ellipse(hMemDC, x - R, y - R, x + R, y + R);	 //공그리기


	hBrush = CreateSolidBrush(RGB(255, 255, 0));
	OldBrush = (HBRUSH)SelectObject(hMemDC, hBrush);
	Rectangle(hMemDC, sX[0], sY[0], sX[0] + W, sY[0] + H); // Left stick
	//Rectangle(hMemDC, sX[1], sY[1], sX[1] + W, sY[1] + H); // Right stick


	DeleteObject(SelectObject(hMemDC, OldPen));
	DeleteObject(SelectObject(hMemDC, OldBrush));

	wsprintf(str, TEXT("%d, %d, %d, %d"), x, y, xv, yv);
	TextOut(hMemDC, 100, 50, str, lstrlen(str));


	SelectObject(hMemDC, OldBit);
	DeleteDC(hMemDC);
	ReleaseDC(hWnd, hdc);
	InvalidateRect(hWnd, NULL, FALSE);
}

void moveBall() {
	x += (int)xv;
	y += (int)yv;
	if (x < crt.left - R) {// When the ball got to the left
		x += R / 2;
		xv *= (-BOUNCE);
	}
	else if (x > crt.right + R) { // When the ball has gotten to the right
		without_ball = 1;
		ball_information->y = y;
		ball_information->xv = xv;
		ball_information->yv = yv;
		ball_information->ball_sent_to_2 = true;
	}
	if (y <= R || y >= crt.bottom - R) {
		yv *= -(BOUNCE);
		if (y <= R) y = R;
		if (y >= crt.bottom - R) y = crt.bottom - R;
	}
}
void moveStick()
{
	RECT crt;
	GetClientRect(hWndMain, &crt);
	if (sY[0] <= 0 || sY[0] >= crt.bottom - H) // left stick
	{
		sYv[0] *= -1;
	}
	sY[0] += sYv[0];

}
void collision() // Collision to a stick
{
	if (x < W + R && y > sY[0] - R && y < sY[0] + H + R) // Left stick
	{
		x += R / 2;
		xv *= (-BOUNCE);
	}
}