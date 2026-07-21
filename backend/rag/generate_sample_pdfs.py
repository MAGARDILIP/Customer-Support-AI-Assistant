"""
Generate realistic sample PDF documents for demonstration.
Creates Return Policy, Shipping Policy, FAQ, and Warranty Policy PDFs.
"""
import os
import logging
from pathlib import Path
from fpdf import FPDF

logger = logging.getLogger(__name__)

SAMPLE_DIR = Path(__file__).parent.parent.parent / "data" / "sample_pdfs"


class PolicyPDF(FPDF):
    """Custom PDF class with consistent styling."""

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, "ShopEase E-Commerce", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 123, 255)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"ShopEase Policies - Page {self.page_no()}/{{nb}}", align="C")

    def add_title(self, title: str):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 123, 255)
        self.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def add_section(self, heading: str):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(33, 37, 41)
        self.cell(0, 8, heading, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def add_body(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(73, 80, 87)
        self.multi_cell(0, 6, text)
        self.ln(3)


def generate_return_policy():
    """Generate Return & Refund Policy PDF."""
    pdf = PolicyPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.add_title("Return & Refund Policy")
    pdf.add_body("Last Updated: January 2025\nThis policy outlines the terms and conditions for returns and refunds at ShopEase.")

    pdf.add_section("1. Return Eligibility")
    pdf.add_body(
        "Customers may return most items purchased from ShopEase within 30 calendar days of delivery. "
        "To be eligible for a return, the item must be unused, in its original packaging, and in the same "
        "condition as when received. Items must include all original tags, accessories, and documentation.\n\n"
        "The 30-day return window begins from the date the item is marked as 'Delivered' in our system."
    )

    pdf.add_section("2. Non-Returnable Items")
    pdf.add_body(
        "The following items cannot be returned:\n"
        "- Digital products (eBooks, online courses, software licenses, apps)\n"
        "- Gift cards and vouchers\n"
        "- Perishable goods (food, beverages, flowers)\n"
        "- Personal care items (opened cosmetics, hygiene products)\n"
        "- Customized or personalized items\n"
        "- Items marked as 'Final Sale' or 'Non-Returnable' on the product page\n"
        "- Undergarments and swimwear for hygiene reasons"
    )

    pdf.add_section("3. Damaged or Defective Items")
    pdf.add_body(
        "If you receive a damaged, defective, or incorrect item, please contact us within 48 hours of delivery. "
        "Damaged items are eligible for return or replacement regardless of the standard 30-day return window. "
        "Please provide photos of the damage and the packaging. We will arrange a free return pickup and "
        "provide a full refund or replacement at no additional cost."
    )

    pdf.add_section("4. Refund Process")
    pdf.add_body(
        "Once your return is received and inspected, we will send you an email notification regarding the "
        "approval or rejection of your refund.\n\n"
        "If approved, your refund will be processed within 5-7 business days:\n"
        "- Credit/Debit Card: Refund credited to original card (3-5 business days after processing)\n"
        "- UPI/Net Banking: Refund to original payment method (2-3 business days)\n"
        "- Cash on Delivery: Refund issued as store credit or bank transfer\n"
        "- Wallet Payment: Instant refund to wallet balance\n\n"
        "Shipping charges are non-refundable unless the return is due to our error."
    )

    pdf.add_section("5. Return Shipping")
    pdf.add_body(
        "For standard returns (change of mind, item doesn't fit), the customer is responsible for return "
        "shipping costs. A flat return shipping fee of $5.99 will be deducted from the refund amount.\n\n"
        "For returns due to our error (wrong item, defective product, damage during shipping), "
        "ShopEase will cover all return shipping costs and arrange a pickup at your convenience."
    )

    pdf.add_section("6. Exchange Policy")
    pdf.add_body(
        "We offer free exchanges for size or color changes on eligible items within the 30-day return window. "
        "If the desired exchange item is a different price, the difference will be charged or refunded accordingly. "
        "To initiate an exchange, contact our support team with your order number and preferred replacement."
    )

    pdf.add_section("7. Late or Missing Refunds")
    pdf.add_body(
        "If you haven't received your refund after the processing period:\n"
        "1. Check your bank account or credit card statement again\n"
        "2. Contact your credit card company (it may take time for the refund to post)\n"
        "3. Contact your bank (there is often processing time before a refund is posted)\n"
        "4. If you've done all of this and still haven't received your refund, contact us at support@shopease.com"
    )

    output_path = SAMPLE_DIR / "return_policy.pdf"
    pdf.output(str(output_path))
    logger.info(f"Generated: {output_path}")
    return str(output_path)


def generate_shipping_policy():
    """Generate Shipping Policy PDF."""
    pdf = PolicyPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.add_title("Shipping & Delivery Policy")
    pdf.add_body("Last Updated: January 2025\nThis policy covers shipping options, delivery times, and tracking information for ShopEase orders.")

    pdf.add_section("1. Shipping Options & Delivery Times")
    pdf.add_body(
        "ShopEase offers the following shipping options:\n\n"
        "Standard Shipping (Free on orders over $50):\n"
        "- Delivery: 5-7 business days\n"
        "- Cost: $4.99 (free for orders over $50)\n\n"
        "Express Shipping:\n"
        "- Delivery: 2-3 business days\n"
        "- Cost: $9.99\n\n"
        "Next-Day Delivery:\n"
        "- Delivery: 1 business day (order before 2 PM)\n"
        "- Cost: $14.99\n"
        "- Available in select metro areas only\n\n"
        "Digital Products:\n"
        "- Instant delivery via email after payment confirmation"
    )

    pdf.add_section("2. Order Processing")
    pdf.add_body(
        "Orders are processed within 1-2 business days after payment confirmation. "
        "Business days are Monday through Friday, excluding public holidays.\n\n"
        "Order status progression:\n"
        "1. Pending - Order received and payment being verified\n"
        "2. Processing - Order confirmed, being prepared for shipment\n"
        "3. Shipped - Order dispatched, tracking number assigned\n"
        "4. Delivered - Order successfully delivered to the address"
    )

    pdf.add_section("3. Order Tracking")
    pdf.add_body(
        "Once your order ships, you will receive an email with your tracking number. "
        "You can track your order:\n"
        "- Through our website using your order number\n"
        "- Via the tracking link in your shipping confirmation email\n"
        "- By contacting our customer support with your order number\n\n"
        "Tracking numbers are typically formatted as TRK followed by 10 alphanumeric characters."
    )

    pdf.add_section("4. International Shipping")
    pdf.add_body(
        "We currently ship to the United States, Canada, United Kingdom, Australia, and select European countries.\n\n"
        "International shipping details:\n"
        "- Delivery: 10-15 business days\n"
        "- Cost: Calculated at checkout based on weight and destination\n"
        "- Customs duties and taxes are the responsibility of the customer\n"
        "- Some items may not be eligible for international shipping"
    )

    pdf.add_section("5. Delivery Issues")
    pdf.add_body(
        "If your package is lost, delayed, or delivered to the wrong address:\n"
        "1. Check the tracking information for the latest status\n"
        "2. Wait 48 hours after the estimated delivery date (packages may be delayed)\n"
        "3. Contact our support team with your order number\n"
        "4. We will investigate with the carrier and provide a resolution within 3 business days\n\n"
        "For packages marked as delivered but not received, we require a 48-hour waiting period "
        "before filing a lost package claim."
    )

    pdf.add_section("6. Address Changes")
    pdf.add_body(
        "Address changes can only be made if the order status is still 'Pending' or 'Processing'. "
        "Once an order has been shipped, the delivery address cannot be changed. "
        "Contact customer support immediately if you need to update your shipping address."
    )

    output_path = SAMPLE_DIR / "shipping_policy.pdf"
    pdf.output(str(output_path))
    logger.info(f"Generated: {output_path}")
    return str(output_path)


def generate_faq():
    """Generate FAQ PDF."""
    pdf = PolicyPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.add_title("Frequently Asked Questions (FAQ)")
    pdf.add_body("Last Updated: January 2025\nFind answers to the most common questions about shopping at ShopEase.")

    pdf.add_section("Account & Orders")

    pdf.add_body(
        "Q: How do I create an account?\n"
        "A: Click 'Sign Up' on our homepage. You can register with your email address or sign in with Google/Facebook. "
        "Account creation is free and gives you access to order tracking, wishlists, and exclusive deals.\n\n"
        "Q: How do I track my order?\n"
        "A: Go to 'My Orders' in your account dashboard or use the tracking number from your shipping confirmation email. "
        "You can also contact our support team with your order number for a status update.\n\n"
        "Q: Can I cancel my order?\n"
        "A: Orders can be cancelled if they are still in 'Pending' or 'Processing' status. "
        "Once an order has been shipped, it cannot be cancelled but can be returned after delivery. "
        "To cancel, go to 'My Orders' and click 'Cancel Order', or contact support.\n\n"
        "Q: Can I modify my order after placing it?\n"
        "A: Order modifications (quantity, size, color) are possible only while the order is in 'Pending' status. "
        "Contact customer support within 1 hour of placing your order for the best chance of modification."
    )

    pdf.add_section("Payments & Pricing")
    pdf.add_body(
        "Q: What payment methods do you accept?\n"
        "A: We accept Visa, MasterCard, American Express, PayPal, Apple Pay, Google Pay, "
        "UPI, Net Banking, and Cash on Delivery (available in select areas).\n\n"
        "Q: Is it safe to use my credit card on ShopEase?\n"
        "A: Absolutely. All transactions are encrypted using 256-bit SSL encryption. "
        "We are PCI-DSS compliant and never store your full card details.\n\n"
        "Q: Do you offer price matching?\n"
        "A: We offer a price match guarantee within 7 days of purchase. If you find the same item "
        "at a lower price from an authorized retailer, contact us with proof and we will refund the difference.\n\n"
        "Q: Are there any hidden fees?\n"
        "A: No. The price shown on the product page is the price you pay, plus applicable shipping fees "
        "shown at checkout. There are no hidden charges."
    )

    pdf.add_section("Returns & Refunds")
    pdf.add_body(
        "Q: How do I return an item?\n"
        "A: Go to 'My Orders', select the order, and click 'Return Item'. Follow the instructions "
        "to print a return label and ship the item back. Alternatively, contact our support team.\n\n"
        "Q: How long does a refund take?\n"
        "A: Refunds are processed within 5-7 business days after we receive and inspect the returned item. "
        "The credit may take an additional 3-5 business days to appear in your account.\n\n"
        "Q: Can I return a digital product?\n"
        "A: Digital products (eBooks, courses, software) are non-refundable once delivered. "
        "If you experience technical issues, our support team will help resolve them.\n\n"
        "Q: What if I received the wrong item?\n"
        "A: Contact us immediately with photos of the item received. We will arrange a free return pickup "
        "and send the correct item at no additional cost."
    )

    pdf.add_section("Customer Support")
    pdf.add_body(
        "Q: How can I contact customer support?\n"
        "A: You can reach us through:\n"
        "- Live Chat: Available 24/7 on our website\n"
        "- Email: support@shopease.com (response within 24 hours)\n"
        "- Phone: 1-800-SHOPEASE (Mon-Sat, 9 AM - 9 PM EST)\n"
        "- Social Media: @ShopEase on Twitter, Facebook, Instagram\n\n"
        "Q: What are your customer support hours?\n"
        "A: Our AI assistant is available 24/7. Human agents are available Monday through Saturday, "
        "9 AM to 9 PM Eastern Time.\n\n"
        "Q: How do I file a complaint?\n"
        "A: We take complaints seriously. Email complaints@shopease.com with your order number "
        "and details. Our team will respond within 24 hours and aim to resolve issues within 48 hours."
    )

    output_path = SAMPLE_DIR / "faq.pdf"
    pdf.output(str(output_path))
    logger.info(f"Generated: {output_path}")
    return str(output_path)


def generate_warranty_policy():
    """Generate Warranty Policy PDF."""
    pdf = PolicyPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.add_title("Product Warranty Policy")
    pdf.add_body("Last Updated: January 2025\nThis policy covers warranty terms for products sold on ShopEase.")

    pdf.add_section("1. Standard Warranty Coverage")
    pdf.add_body(
        "All physical products sold on ShopEase come with a minimum 1-year standard warranty "
        "against manufacturing defects, unless otherwise stated on the product page.\n\n"
        "Electronics: 1-year manufacturer warranty\n"
        "Clothing & Accessories: 6-month warranty against stitching defects\n"
        "Home & Kitchen: 1-year warranty against manufacturing defects\n"
        "Sports Equipment: 1-year warranty\n"
        "Personal Care: 6-month warranty on electronic components"
    )

    pdf.add_section("2. What is Covered")
    pdf.add_body(
        "The warranty covers:\n"
        "- Manufacturing defects in materials and workmanship\n"
        "- Electronic component failure under normal use\n"
        "- Premature wear beyond expected product lifetime\n"
        "- Functional defects that prevent normal use of the product"
    )

    pdf.add_section("3. What is NOT Covered")
    pdf.add_body(
        "The warranty does NOT cover:\n"
        "- Damage caused by misuse, abuse, or accidents\n"
        "- Normal wear and tear\n"
        "- Damage from unauthorized modifications or repairs\n"
        "- Water damage (unless product is rated as waterproof)\n"
        "- Cosmetic damage (scratches, dents) that doesn't affect functionality\n"
        "- Damage from natural disasters (fire, flood, lightning)\n"
        "- Products used for commercial purposes (unless specified)"
    )

    pdf.add_section("4. How to Claim Warranty")
    pdf.add_body(
        "To file a warranty claim:\n"
        "1. Contact customer support with your order number and describe the issue\n"
        "2. Provide photos or video of the defect\n"
        "3. Our team will assess the claim within 3 business days\n"
        "4. If approved, we will provide a prepaid shipping label for return\n"
        "5. After inspection, we will repair, replace, or refund the product\n\n"
        "Please retain your order confirmation email as proof of purchase."
    )

    pdf.add_section("5. Extended Warranty")
    pdf.add_body(
        "ShopEase offers an optional Extended Warranty plan for electronics and appliances:\n\n"
        "- ShopEase Protect 2-Year: $19.99 - Extends coverage to 2 years total\n"
        "- ShopEase Protect 3-Year: $29.99 - Extends coverage to 3 years total\n"
        "- Includes accidental damage protection\n"
        "- One-time screen replacement for tablets and smartwatches\n"
        "- Priority support queue for warranty claims\n\n"
        "Extended warranty must be purchased within 30 days of the original product purchase."
    )

    output_path = SAMPLE_DIR / "warranty_policy.pdf"
    pdf.output(str(output_path))
    logger.info(f"Generated: {output_path}")
    return str(output_path)


def generate_all_sample_pdfs() -> list[str]:
    """Generate all sample PDF documents. Returns list of file paths."""
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    paths = []
    generators = [
        generate_return_policy,
        generate_shipping_policy,
        generate_faq,
        generate_warranty_policy,
    ]
    for gen in generators:
        try:
            path = gen()
            paths.append(path)
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")

    logger.info(f"Generated {len(paths)} sample PDFs in {SAMPLE_DIR}")
    return paths


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_all_sample_pdfs()
