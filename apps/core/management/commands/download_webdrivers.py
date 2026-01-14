"""
Django管理命令：预下载所有WebDriver
用法：python manage.py download_webdrivers
"""
from django.core.management.base import BaseCommand
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time


class Command(BaseCommand):
    help = '预下载所有浏览器的WebDriver驱动程序'

    def add_arguments(self, parser):
        parser.add_argument(
            '--browsers',
            nargs='+',
            default=['chrome', 'firefox', 'edge'],
            help='指定要下载驱动的浏览器，默认下载所有'
        )

    def handle(self, *args, **options):
        browsers = options['browsers']

        self.stdout.write(self.style.SUCCESS('开始下载WebDriver驱动程序...'))
        self.stdout.write(self.style.WARNING('注意：首次下载可能需要几分钟时间\n'))

        success_count = 0
        failed_browsers = []

        if 'chrome' in browsers:
            self.stdout.write('正在下载 ChromeDriver...')
            try:
                start_time = time.time()
                driver_path = ChromeDriverManager().install()
                elapsed = time.time() - start_time
                self.stdout.write(self.style.SUCCESS(
                    f'✓ ChromeDriver 下载成功 (耗时: {elapsed:.1f}秒)'
                ))
                self.stdout.write(f'  路径: {driver_path}\n')
                success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ ChromeDriver 下载失败: {str(e)}\n'))
                failed_browsers.append(('Chrome', str(e)))

        if 'firefox' in browsers:
            self.stdout.write('正在下载 GeckoDriver (Firefox)...')
            try:
                start_time = time.time()
                driver_path = GeckoDriverManager().install()
                elapsed = time.time() - start_time
                self.stdout.write(self.style.SUCCESS(
                    f'✓ GeckoDriver 下载成功 (耗时: {elapsed:.1f}秒)'
                ))
                self.stdout.write(f'  路径: {driver_path}\n')
                success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ GeckoDriver 下载失败: {str(e)}\n'))
                failed_browsers.append(('Firefox', str(e)))

        if 'edge' in browsers:
            self.stdout.write('正在下载 EdgeDriver...')
            try:
                start_time = time.time()
                driver_path = EdgeChromiumDriverManager().install()
                elapsed = time.time() - start_time
                self.stdout.write(self.style.SUCCESS(
                    f'✓ EdgeDriver 下载成功 (耗时: {elapsed:.1f}秒)'
                ))
                self.stdout.write(f'  路径: {driver_path}\n')
                success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ EdgeDriver 下载失败: {str(e)}\n'))
                failed_browsers.append(('Edge', str(e)))

        # 总结
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'\n下载完成！成功: {success_count}个'))

        if failed_browsers:
            self.stdout.write(self.style.ERROR(f'失败: {len(failed_browsers)}个'))
            for browser, error in failed_browsers:
                self.stdout.write(f'  - {browser}: {error}')

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('\n驱动程序已缓存，后续测试执行将会更快！'))
