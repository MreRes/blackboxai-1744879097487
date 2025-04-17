class IndonesianCommands:
    """Indonesian language command mappings and responses"""
    
    # Command mappings (formal and informal)
    COMMANDS = {
        # Expense commands
        'pengeluaran': 'expense',
        'keluar': 'expense',
        'bayar': 'expense',
        'beli': 'expense',
        
        # Income commands
        'pemasukan': 'income',
        'masuk': 'income',
        'gajian': 'income',
        'terima': 'income',
        
        # Balance commands
        'saldo': 'balance',
        'ceksaldo': 'balance',
        'uang': 'balance',
        'duit': 'balance',
        
        # Report commands
        'laporan': 'report',
        'report': 'report',
        'rekap': 'report',
        'rangkuman': 'report',
        
        # Financial planning commands
        'rencana': 'plan',
        'rencanakan': 'plan',
        'planning': 'plan',
        'konsultasi': 'plan',
        'saran': 'plan',
        'advice': 'plan',
        
        # Investment commands
        'investasi': 'invest',
        'saham': 'invest',
        'reksadana': 'invest',
        'obligasi': 'invest',
        
        # Savings goal commands
        'target': 'goal',
        'tabungan': 'goal',
        'nabung': 'goal',
        'simpanan': 'goal',
        
        # Budget commands
        'budget': 'budget',
        'anggaran': 'budget',
        'atur': 'budget',
        'rencanabiaya': 'budget',
        
        # Market info commands
        'pasar': 'market',
        'ihsg': 'market',
        'kurs': 'market',
        'market': 'market',
        
        # Help commands
        'bantuan': 'help',
        'tolong': 'help',
        'help': 'help',
        'cara': 'help'
    }

    # Categories in Indonesian
    EXPENSE_CATEGORIES = {
        'makan': 'food',
        'makanan': 'food',
        'transport': 'transportation',
        'transportasi': 'transportation',
        'bensin': 'transportation',
        'rumah': 'housing',
        'kost': 'housing',
        'sewa': 'housing',
        'listrik': 'utilities',
        'air': 'utilities',
        'internet': 'utilities',
        'pulsa': 'utilities',
        'kesehatan': 'healthcare',
        'dokter': 'healthcare',
        'obat': 'healthcare',
        'hiburan': 'entertainment',
        'nonton': 'entertainment',
        'game': 'entertainment',
        'belanja': 'shopping',
        'baju': 'shopping',
        'pendidikan': 'education',
        'kursus': 'education',
        'sekolah': 'education',
        'tabungan': 'savings',
        'nabung': 'savings',
        'lainnya': 'other'
    }

    INCOME_CATEGORIES = {
        'gaji': 'salary',
        'salary': 'salary',
        'bisnis': 'business',
        'usaha': 'business',
        'dagang': 'business',
        'investasi': 'investment',
        'saham': 'investment',
        'freelance': 'freelance',
        'proyek': 'freelance',
        'lainnya': 'other'
    }

    @staticmethod
    def get_help_message():
        return """🤖 *Bot Keuangan AI - Perintah yang Tersedia*:

• Pencatatan Keuangan:
  ➤ Catat Pengeluaran:
    pengeluaran <jumlah> [kategori] [keterangan]
    Contoh: pengeluaran 50000 makan siang
    Informal: bayar 50000 makan

  ➤ Catat Pemasukan:
    pemasukan <jumlah> [kategori] [keterangan]
    Contoh: pemasukan 1000000 gaji bulanan
    Informal: masuk 1000000 gaji

• Informasi Saldo & Laporan:
  ➤ Cek Saldo:
    saldo, ceksaldo, uang, duit

  ➤ Lihat Laporan:
    laporan, rekap, rangkuman

• Perencanaan Keuangan:
  ➤ Konsultasi Keuangan:
    rencana, konsultasi, saran
    Contoh: rencana keuangan bulanan

  ➤ Informasi Investasi:
    investasi, saham, reksadana
    Contoh: investasi saham pemula

  ➤ Target Tabungan:
    target <jumlah> [nama_target] [tenggat]
    Contoh: target 10000000 liburan 6bulan

  ➤ Atur Budget:
    budget, anggaran
    Contoh: budget bulanan

  ➤ Info Pasar:
    pasar, ihsg, kurs
    Contoh: kurs dollar

• Bantuan:
  bantuan, tolong, help, cara

*Kategori Pengeluaran*:
- makan/makanan
- transport/transportasi/bensin
- rumah/kost/sewa
- listrik/air/internet/pulsa
- kesehatan/dokter/obat
- hiburan/nonton/game
- belanja/baju
- pendidikan/kursus/sekolah
- tabungan/nabung
- lainnya

*Kategori Pemasukan*:
- gaji/salary
- bisnis/usaha/dagang
- investasi/saham
- freelance/proyek
- lainnya

*Tips*:
• Gunakan perintah 'rencana' untuk mendapatkan saran keuangan personal
• Cek 'pasar' untuk informasi terkini IHSG dan kurs
• Tetapkan target tabungan dengan perintah 'target'
• Evaluasi pengeluaran secara rutin dengan 'laporan'"""

    @staticmethod
    def format_currency(amount):
        """Format amount in Indonesian Rupiah"""
        return f"Rp {amount:,.0f}".replace(',', '.')

    @staticmethod
    def get_success_message(transaction_type, amount, category, description=None):
        """Get success message in Indonesian"""
        if transaction_type == 'expense':
            msg = f"✅ Pengeluaran tercatat:\nJumlah: {IndonesianCommands.format_currency(amount)}\nKategori: {category}"
        else:
            msg = f"✅ Pemasukan tercatat:\nJumlah: {IndonesianCommands.format_currency(amount)}\nKategori: {category}"
        
        if description:
            msg += f"\nKeterangan: {description}"
        return msg

    @staticmethod
    def get_error_message():
        """Get error message in Indonesian"""
        return "❌ Format tidak valid. Ketik 'bantuan' untuk melihat cara penggunaan."

    @staticmethod
    def get_balance_message(amount):
        """Get balance message in Indonesian"""
        return f"💰 Saldo Anda: {IndonesianCommands.format_currency(amount)}"

    @staticmethod
    def translate_command(text):
        """Translate Indonesian command to English"""
        words = text.lower().split()
        if not words:
            return None, []
        
        command = words[0]
        params = words[1:]
        
        # Translate command
        english_command = IndonesianCommands.COMMANDS.get(command)
        if not english_command:
            return None, []
        
        # Translate category if present
        if len(params) >= 2:
            category = params[1]
            if english_command == 'expense':
                english_category = IndonesianCommands.EXPENSE_CATEGORIES.get(category)
                if english_category:
                    params[1] = english_category
            elif english_command == 'income':
                english_category = IndonesianCommands.INCOME_CATEGORIES.get(category)
                if english_category:
                    params[1] = english_category
        
        return english_command, params
