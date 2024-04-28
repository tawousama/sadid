from odoo import api, fields, models, _


class NewModel(models.Model):
    _name = 'new.model'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "New Model"

    request = fields.Selection(string='نوع التسهيلات',
                               selection=[('a', ' تسهيلات جديدة'), ('b', 'تجديد التسهيلات')])

    sector = fields.Selection(string='القطاع',
                              selection=[('c', ' عام '), ('d', ' خاص ')])

    activity = fields.Char(string='النشاط')
    branch = fields.Char(string='الفرع')
    account_number = fields.Char(string='رقم الحساب')
    account_opening_date = fields.Date(string='تاريخ فتح الحساب')
    company_name = fields.Char(string='التسمية الكاملة')
    company_branch = fields.Char(string='فرع')
    company_acronym = fields.Char(string='اختصار')
    company_phone = fields.Char(string='الهاتف')
    company_fax = fields.Char(string='فاكس')
    company_email = fields.Char(string='البريد الالكتروني')
    legal_form = fields.Char(string='الشكل القانوني')
    company_capital = fields.Float(string='رأس مال الشركة')
    origin_date = fields.Date(string='تاريخ النشأة')
    start_date = fields.Date(string='تاريخ بداية النشاط')
    register_no = fields.Integer(string='تسجيل في السجل التجاري رقم')
    register_date = fields.Date(string='بتاريخ')
    register_in = fields.Char(string='في')
    headquarter_address = fields.Char(string='عنوان المقر الرئيسي')
    legal_nature = fields.Selection(string=' ',
                                    selection=[('e', ' ملكية '), ('f', ' إيجار')])
    location_production = fields.Char(string='مكان تواجد وحدة الإنتاج')
    legal_nature_for_land = fields.Char(string='الطبيعة القانونية لقطعة الأرض المشيد عليها المصنع و كذا المساحة')
    main_activity = fields.Char(string='نشاط رئيسي')
    secondary_activity = fields.Char(string='نشاط ثانوي')
    production_capacity = fields.Char(string='قدرة الإنتاج')
    quantity = fields.Float(string='الكمية')
    value = fields.Float(string='القيمة')
    quantity2 = fields.Float(string='الكمية')
    value2 = fields.Float(string='القيمة')
    nature_of_goods_sold = fields.Char(string='طبيعة السلع المباعة (نشاط التداول)')
    nature_of_goods_manufacturer = fields.Char(string='طبيعة المنتجات المصنعة')
    provision_of_services = fields.Char(string='تقديم الخدمات (نشاط الخدمات)')
    building = fields.Char(string='البناء، الأشغال العمومية و الري ( نشاط الإنجازات)')
    facilitators = fields.Char(string='المسيرون')
    name_of_owner = fields.Char(string='اسم و لقب المالك (شركة شخصية أو ذات الشخص الوحيد)')
    name_of_director = fields.Char(string='اسم و لقب رئيس المدير العام أو المدير العام')
    name_of_facilitator = fields.Char(string='اسم و لقب المسير')
    age = fields.Integer(string='السن')
    scientific = fields.Char(string='المستوى العلمي (التكوين)')
    professional_experience = fields.Char(string='التجربة المهنية')
    name_of_financial_manager = fields.Char(string='اسم المدير المالي ')
    number_of_workers = fields.Char(string='عدد العمال')
    tires = fields.Char(string='اطارات')
    supervisors = fields.Char(string='مشرفين')
    two_applicators = fields.Char(string='مطبقين')
    payroll = fields.Float(string='حجم الرواتب السنوي (دج)')
    land_ids = fields.Many2many('lands.buildings', string=' أراضي و مباني الاستغلال ')
    hardware_ids = fields.Many2many('exploitation.equipment', string=' معدات الاستغلال ')
    partner_ids = fields.Many2many('real.estate', string=' معدات الاستغلال ')
    company_ids = fields.Many2many('other.companies', string=' معدات الاستغلال ')
    purchases_ids = fields.Many2many('purchases.activity', string='المشتريات')
    sales_ids = fields.Many2many('sales.activity', string='المبيعات')
    facilitie_ids = fields.Many2many('facilities.type', string='التسهيلات')
    security_ids = fields.Many2many('proposed.guarantees', string='الضمانات')
    obligations_ids = fields.Many2many('obligations.banks', string='الالتزامات')

    def create_report_peace_bank(self):
        return self.env.ref('credit_bancaire.report_peace_bank_id').report_action(self)


class LandsBuildings(models.Model):
    _name = 'lands.buildings'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Lands Buildings"

    nature_of_origin = fields.Char(string='طبيعة الأصل')
    address = fields.Char(string='العنوان و الرقم العقاري')
    total_area = fields.Char(string='المساحة الإجمالية (أراضي)')
    under_foreclosure = fields.Selection(string='تحت الرهن',
                                         selection=[('no', ' لا'), ('yes', 'نعم')])
    owner = fields.Selection(string='مالك أو مستأجر',
                             selection=[('q', ' ك '), ('g', ' ج ')])


class ExploitationEquipment(models.Model):
    _name = 'exploitation.equipment'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Exploitation Equipment"

    hardware = fields.Char(string='المعدات')
    year_of_acquisition = fields.Integer(string='سنة الاقتناء')
    acquisition_value = fields.Float(string='قيمة الاقتناء')
    note = fields.Char(string='ملاحظة')


class RealEstate(models.Model):
    _name = 'real.estate'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Real Estate"

    partner = fields.Char(string='شركاء / مساهمين')
    nature_of_real_estate = fields.Char(string='طبيعة الملكية العقارية')
    estimated_value = fields.Float(string='القيمة التقديرية')
    mortgage_creditors = fields.Char(string='الدائنين بالرهن')


class OtherCompanies(models.Model):
    _name = 'other.companies'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "OtherCompanies"

    names_of_partners = fields.Char(string='أسماء الشركاء')
    company_in = fields.Many2many('companies.in', string='شركات موطنة لدى مصرف السلام')
    company_out = fields.Many2many('companies.out', string='شركات موطنة لدى البنوك الأخرى')


class CompaniesIn(models.Model):
    _name = 'companies.in'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Companies In"

    the_company_name = fields.Char(string='اسم الشركة')
    obligations = fields.Char(string='الالتزامات')


class CompaniesOut(models.Model):
    _name = 'companies.out'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Companies Out"

    the_company_name_o = fields.Char(string='اسم الشركة')
    obligations_o = fields.Char(string='الالتزامات')


class PurchasesActivity(models.Model):
    _name = 'purchases.activity'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Purchases Activity"

    purchases = fields.Char(string='المشتريات')
    suppliers = fields.Many2many('purchases.suppliers', string='الموردون')
    payment_method = fields.Char(string='طريقة الدفع')


class PurchasesSuppliers(models.Model):
    _name = 'purchases.suppliers'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Purchases Suppliers"

    aliens = fields.Many2many('purchases.aliens', string='الأجانب')
    local = fields.Many2many('purchases.local', string='المحليين')


class PurchasesAliens(models.Model):
    _name = 'purchases.aliens'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Purchases Aliens"

    country = fields.Char(string='ألف دج')
    a_thousand_dzd = fields.Char(string='ألف دج')


class PurchasesLocal(models.Model):
    _name = 'purchases.local'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Purchases Local"

    l_name = fields.Char(string='الاسم')
    l_thousand_dzd = fields.Char(string='ألف دج')


class SalesActivity(models.Model):
    _name = 'sales.activity'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "sales Activity"

    sales = fields.Char(string='المبيعات')
    suppliers_s = fields.Many2many('sales.suppliers', string='الزبائن')
    collection_method = fields.Char(string='طريقة التحصيل')


class SalesSuppliers(models.Model):
    _name = 'sales.suppliers'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "sales Suppliers"

    s_aliens = fields.Many2many('sales.aliens', string='الأجانب')
    s_local = fields.Many2many('sales.local', string='المحليين')


class SalesAliens(models.Model):
    _name = 'sales.aliens'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "sales Aliens"

    s_country = fields.Char(string='ألف دج')
    s_a_thousand_dzd = fields.Char(string='ألف دج')


class SalesLocal(models.Model):
    _name = 'sales.local'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "sales Local"

    s_l_name = fields.Char(string='الاسم')
    s_l_thousand_dzd = fields.Char(string='ألف دج')


class FacilitiesType(models.Model):
    _name = 'facilities.type'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Facilities Type"

    f_type = fields.Char(string='نوع التسهيلات')
    amounts_required = fields.Many2many('amounts.required', string='المبالغ المطلوبة')


class AmountsRequired(models.Model):
    _name = 'amounts.required'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Amounts Required"

    in_dinars = fields.Float(string='بالدينار')
    in_hard_currency = fields.Float(string='بالعملة الصعبة')


class ProposedGuarantees(models.Model):
    _name = 'proposed.guarantees'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Proposed Guarantees"

    nature_of_guarantee = fields.Char(string='طبيعة الضمان')
    collateral_value = fields.Float(string='قيمة الضمان')


class ObligationsBanks(models.Model):
    _name = 'obligations.banks'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Obligations Banks"

    bank = fields.Char(string='البنك')
    guarantees_provided = fields.Char(string='الضمانات المقدمة')
    total_liabilities = fields.Float(string='مجموع الالتزامات')
