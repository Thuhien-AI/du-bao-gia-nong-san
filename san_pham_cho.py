# -*- coding: utf-8 -*-
"""
Danh sách sản phẩm MẪU của "Chợ nông nghiệp" trong Diễn đàn.

- Chỉ dùng để tạo sẵn hàng lần đầu chạy web (khi bảng sản phẩm còn trống).
- Sau đó tài khoản quản trị (admin) thêm / sửa / ẩn sản phẩm ngay trên web,
  nên sửa file này KHÔNG làm đổi sản phẩm đã có.
- Giá dưới đây là GIÁ MẪU để trình bày, chưa phải giá bán thật.
"""

DANH_MUC = ["Phân bón", "Thuốc trừ sâu", "Hạt giống", "Dụng cụ"]

SAN_PHAM_MAU = [
    # (tên, danh mục, giá (đồng), đơn vị, mô tả ngắn, hợp với cây)
    ("Phân NPK 16-16-8", "Phân bón", 820_000, "bao 50 kg",
     "Phân hỗn hợp cân đối đạm – lân – kali, bón thúc giai đoạn cây sinh trưởng mạnh.", "Lúa, Cà phê, Hồ tiêu"),
    ("Phân Urê 46%", "Phân bón", 650_000, "bao 50 kg",
     "Đạm hạt đục, giúp cây xanh lá, đẻ nhánh khỏe. Chia nhỏ lượng bón nhiều lần.", "Lúa"),
    ("Phân hữu cơ vi sinh", "Phân bón", 210_000, "bao 40 kg",
     "Cải tạo đất, tăng mùn và vi sinh vật có ích, giúp rễ phát triển.", "Cà phê, Hồ tiêu"),
    ("Phân bón lá kích ra hoa", "Phân bón", 85_000, "chai 500 ml",
     "Bổ sung vi lượng Bo, Kẽm giúp cây ra hoa đều, đậu trái tốt.", "Cà phê, Hồ tiêu"),
    ("Thuốc trừ rầy nâu", "Thuốc trừ sâu", 45_000, "gói 100 g",
     "Phòng trừ rầy nâu, rầy lưng trắng hại lúa. Đọc kỹ nhãn trước khi dùng.", "Lúa"),
    ("Thuốc trừ sâu sinh học Bt", "Thuốc trừ sâu", 55_000, "gói 100 g",
     "Nguồn gốc sinh học, an toàn hơn cho thiên địch, trị sâu cuốn lá, sâu ăn lá.", "Lúa, Cà phê"),
    ("Thuốc trị nấm bệnh", "Thuốc trừ sâu", 120_000, "chai 500 ml",
     "Phòng trị nấm gây đạo ôn, khô vằn, rỉ sắt. Phun khi bệnh mới chớm.", "Lúa, Cà phê"),
    ("Chế phẩm trị tuyến trùng rễ", "Thuốc trừ sâu", 160_000, "gói 1 kg",
     "Chế phẩm sinh học hỗ trợ hạn chế tuyến trùng và nấm hại rễ hồ tiêu.", "Hồ tiêu"),
    ("Lúa giống ST25", "Hạt giống", 350_000, "bao 10 kg",
     "Giống lúa thơm, hạt dài, cơm dẻo. Hạt giống cấp xác nhận.", "Lúa"),
    ("Lúa giống OM5451", "Hạt giống", 220_000, "bao 10 kg",
     "Giống ngắn ngày, năng suất ổn định, thích nghi nhiều vùng đồng bằng.", "Lúa"),
    ("Cây giống cà phê Robusta ghép", "Hạt giống", 12_000, "cây",
     "Cây ghép khoẻ, chiều cao 25–30 cm, sẵn sàng trồng đầu mùa mưa.", "Cà phê"),
    ("Hom tiêu Vĩnh Linh", "Hạt giống", 15_000, "bầu",
     "Hom tiêu ươm sẵn trong bầu, rễ khoẻ, sạch bệnh.", "Hồ tiêu"),
    ("Bình phun điện 16 lít", "Dụng cụ", 690_000, "cái",
     "Bình đeo vai chạy pin, phun đều, đỡ mỏi tay khi phun thuốc và phân bón lá.", "Lúa, Cà phê, Hồ tiêu"),
    ("Kéo cắt cành", "Dụng cụ", 95_000, "cái",
     "Lưỡi thép sắc, tay cầm chống trượt, dùng tỉa cành cà phê và hồ tiêu.", "Cà phê, Hồ tiêu"),
]


# ================================================================ CHI TIẾT · HƯỚNG DẪN SỬ DỤNG · LƯU Ý
# Nạp vào sản phẩm cùng tên nếu sản phẩm đó chưa có nội dung (admin sửa tiếp được trên web).
# Liều lượng chỉ để THAM KHẢO; luôn làm theo nhãn trên bao bì và hướng dẫn của cán bộ khuyến nông địa phương.
CHI_TIET = {
    "Phân NPK 16-16-8": dict(
        chi_tiet="- **Thành phần:** Đạm (N) 16% · Lân (P₂O₅) 16% · Kali (K₂O) 8%\n- **Dạng:** hạt tròn, dễ rải, tan đều\n"
                 "- **Quy cách:** bao 50 kg\n- **Công dụng:** giúp cây ra rễ khỏe, đẻ nhánh, xanh lá và lớn đều; dùng được cho cả bón lót và bón thúc.",
        huong_dan="1. **Lúa:** bón thúc lần 1 khi lúa 7–10 ngày sau sạ, lần 2 lúc lúa đẻ nhánh rộ. Khoảng **100–150 kg/ha mỗi lần**.\n"
                  "2. **Cà phê, hồ tiêu:** bón 3–4 lần trong mùa mưa, khoảng **0,3–0,5 kg/gốc/lần** với cây đang cho trái. "
                  "Rải đều quanh mép tán, cào nhẹ lấp đất.\n3. Bón khi đất đủ ẩm; không bón lúc trời mưa to để phân không bị rửa trôi.",
        luu_y="- Liều lượng chỉ để tham khảo, tuỳ đất và tuổi cây.\n- Đeo găng tay khi rải phân, rửa tay sau khi dùng.\n"
              "- Cất nơi khô ráo, buộc kín miệng bao sau khi dùng."),
    "Phân Urê 46%": dict(
        chi_tiet="- **Thành phần:** Đạm (N) 46%\n- **Dạng:** hạt trắng, tan nhanh trong nước\n- **Quy cách:** bao 50 kg\n"
                 "- **Công dụng:** bổ sung đạm nhanh giúp cây xanh lá, đẻ nhánh, lớn nhanh.",
        huong_dan="1. **Lúa:** chia 2–3 lần bón (đẻ nhánh, làm đòng). Tổng cả vụ khoảng **150–200 kg/ha** tuỳ giống và đất.\n"
                  "2. **Cây trồng cạn:** rải quanh gốc rồi tưới nước, hoặc hoà loãng để tưới.\n"
                  "3. Nên trộn với phân lân, kali để cây cân đối, không bón riêng urê quá nhiều.",
        luu_y="- Bón quá nhiều đạm làm lúa lốp, dễ đổ ngã và nhiễm sâu bệnh.\n- Không rải khi lá còn ướt sương hoặc trời nắng gắt.\n"
              "- Phân dễ hút ẩm: buộc kín bao, để nơi khô."),
    "Phân hữu cơ vi sinh": dict(
        chi_tiet="- **Thành phần:** chất hữu cơ và các vi sinh vật có ích (phân giải lân, phân giải chất xơ…)\n"
                 "- **Dạng:** bột tơi, màu nâu đen\n- **Quy cách:** bao 40 kg\n"
                 "- **Công dụng:** làm đất tơi xốp, tăng mùn, giúp rễ phát triển và cây hấp thu phân tốt hơn.",
        huong_dan="1. **Cà phê, hồ tiêu:** bón **3–5 kg/gốc/năm** vào đầu mùa mưa. Rạch rãnh quanh mép tán, rải phân rồi lấp đất.\n"
                  "2. **Lúa, rau màu:** bón lót trước khi gieo trồng, khoảng **500–1.000 kg/ha**.\n"
                  "3. Có thể trộn với phân NPK khi bón.",
        luu_y="- Không trộn chung với vôi hoặc thuốc trị nấm vì làm chết vi sinh có ích.\n"
              "- Để nơi thoáng mát, tránh nắng trực tiếp.\n- Dùng hết trong thời hạn ghi trên bao."),
    "Phân bón lá kích ra hoa": dict(
        chi_tiet="- **Thành phần:** Bo (B), Kẽm (Zn) và các vi lượng cần cho ra hoa, đậu trái\n- **Dạng:** dung dịch\n"
                 "- **Quy cách:** chai 500 ml\n- **Công dụng:** giúp cây ra hoa đều, hoa khỏe, tăng tỉ lệ đậu trái.",
        huong_dan="1. Lắc đều chai, pha với nước sạch **theo tỉ lệ ghi trên nhãn chai**.\n"
                  "2. Phun 1–2 lần trước khi cây ra hoa khoảng 7–10 ngày.\n"
                  "3. Phun đều cả hai mặt lá vào sáng sớm hoặc chiều mát.",
        luu_y="- Không phun khi hoa đang nở rộ hoặc trời sắp mưa.\n- Không phun đặc hơn hướng dẫn, dễ cháy lá.\n"
              "- Để xa tầm tay trẻ em."),
    "Thuốc trừ rầy nâu": dict(
        chi_tiet="- **Hoạt chất:** Pymetrozine 50% (dạng hạt phân tán WG)\n- **Quy cách:** gói 100 g\n"
                 "- **Công dụng:** trừ rầy nâu, rầy lưng trắng hại lúa; rầy ngưng chích hút sau khi trúng thuốc.",
        huong_dan="1. Thăm đồng thường xuyên, phun khi thấy mật độ rầy cao (rầy non tuổi nhỏ).\n"
                  "2. Pha thuốc **đúng liều ghi trên nhãn**, khuấy đều.\n"
                  "3. Rẽ lúa, phun kỹ vào **phần gốc lúa** nơi rầy tập trung. Phun lúc chiều mát.\n"
                  "4. Áp dụng nguyên tắc **4 đúng**: đúng thuốc, đúng lúc, đúng liều, đúng cách.",
        luu_y="- Mặc đồ bảo hộ, đeo khẩu trang, găng tay khi pha và phun; không ăn uống, hút thuốc khi phun.\n"
              "- Tuân thủ **thời gian cách ly** ghi trên nhãn trước khi thu hoạch.\n"
              "- Không rửa bình phun xuống ao, kênh; thu gom vỏ bao vào nơi quy định.\n- Cất xa thức ăn và tầm tay trẻ em."),
    "Thuốc trừ sâu sinh học Bt": dict(
        chi_tiet="- **Hoạt chất:** vi khuẩn *Bacillus thuringiensis* (Bt)\n- **Quy cách:** gói 100 g\n"
                 "- **Công dụng:** trừ sâu non ăn lá như sâu cuốn lá, sâu xanh, sâu tơ; ít hại thiên địch và ong.",
        huong_dan="1. Phun khi sâu còn **nhỏ tuổi** (mới nở) để hiệu quả cao nhất.\n2. Pha theo **liều ghi trên nhãn**, dùng ngay sau khi pha.\n"
                  "3. Phun vào **chiều mát**, vì ánh nắng làm giảm tác dụng của vi khuẩn.",
        luu_y="- Không pha chung với thuốc gốc đồng hoặc thuốc trị nấm.\n- Vẫn nên đeo khẩu trang, găng tay khi phun.\n"
              "- Bảo quản nơi mát, tránh nắng."),
    "Thuốc trị nấm bệnh": dict(
        chi_tiet="- **Hoạt chất:** Hexaconazole 5% (dạng huyền phù SC)\n- **Quy cách:** chai 500 ml\n"
                 "- **Công dụng:** phòng trị bệnh do nấm như khô vằn, lem lép hạt trên lúa; rỉ sắt trên cà phê.",
        huong_dan="1. Phun khi bệnh **mới chớm** xuất hiện.\n2. Lắc đều chai, pha **đúng liều ghi trên nhãn**.\n"
                  "3. Phun ướt đều thân lá, nhất là nơi có vết bệnh. Bệnh nặng có thể phun lại sau 7–10 ngày.",
        luu_y="- Mặc đồ bảo hộ khi pha và phun.\n- Tuân thủ thời gian cách ly ghi trên nhãn.\n"
              "- Không đổ thuốc thừa xuống nguồn nước.\n- Cất xa tầm tay trẻ em."),
    "Chế phẩm trị tuyến trùng rễ": dict(
        chi_tiet="- **Thành phần:** nấm đối kháng có ích (sinh học)\n- **Quy cách:** gói 1 kg\n"
                 "- **Công dụng:** hạn chế tuyến trùng và nấm hại rễ, giúp bộ rễ hồ tiêu khỏe, ít vàng lá.",
        huong_dan="1. Rải chế phẩm quanh gốc theo **hình chiếu tán cây**, liều theo nhãn.\n"
                  "2. Xới nhẹ cho chế phẩm trộn vào lớp đất mặt, rồi **tưới ẩm**.\n"
                  "3. Dùng 2 lần mỗi năm: đầu mùa mưa và cuối mùa mưa.",
        luu_y="- Không dùng chung với thuốc trị nấm hoá học.\n- Đất cần đủ ẩm để nấm có ích phát triển.\n"
              "- Bảo quản nơi khô mát, dùng trong hạn sử dụng."),
    "Lúa giống ST25": dict(
        chi_tiet="- **Giống:** ST25, hạt giống cấp xác nhận\n- **Thời gian sinh trưởng:** khoảng 95–105 ngày\n"
                 "- **Đặc điểm:** gạo thơm, hạt dài, cơm mềm dẻo\n- **Quy cách:** bao 10 kg",
        huong_dan="1. **Ngâm** hạt giống trong nước sạch 24–36 giờ, thay nước 1–2 lần.\n"
                  "2. **Ủ** 24–36 giờ đến khi hạt nứt nanh, mộng ngắn thì đem gieo.\n"
                  "3. Lượng giống tham khảo: **80–120 kg/ha** (sạ hàng dùng ít hơn sạ lan).",
        luu_y="- Kiểm tra tem nhãn, ngày sản xuất trước khi mua.\n- Giữ bao giống nơi khô thoáng, tránh chuột.\n"
              "- Nên gieo đồng loạt theo lịch thời vụ của địa phương."),
    "Lúa giống OM5451": dict(
        chi_tiet="- **Giống:** OM5451, hạt giống cấp xác nhận\n- **Thời gian sinh trưởng:** khoảng 90–95 ngày\n"
                 "- **Đặc điểm:** ngắn ngày, năng suất ổn định, thích nghi nhiều vùng\n- **Quy cách:** bao 10 kg",
        huong_dan="1. **Ngâm** hạt giống 24–36 giờ, thay nước 1–2 lần.\n2. **Ủ** 24–36 giờ đến khi nứt nanh.\n"
                  "3. Lượng giống tham khảo: **80–120 kg/ha**.",
        luu_y="- Kiểm tra tem nhãn, hạn dùng.\n- Bảo quản nơi khô thoáng.\n- Gieo theo lịch thời vụ địa phương."),
    "Cây giống cà phê Robusta ghép": dict(
        chi_tiet="- **Giống:** cà phê vối (Robusta) ghép từ dòng năng suất cao\n- **Chiều cao cây:** 25–30 cm, 5–6 cặp lá\n"
                 "- **Đơn vị:** 1 cây trong bầu đất\n- **Ưu điểm:** cây ghép sớm cho trái, trái đồng đều.",
        huong_dan="1. Trồng **đầu mùa mưa**. Đào hố khoảng **60 × 60 × 60 cm**, khoảng cách tham khảo 3 × 3 m.\n"
                  "2. Bón lót phân hữu cơ hoai mục trộn với đất mặt cho vào hố.\n"
                  "3. Rạch bỏ túi bầu, đặt bầu ngang mặt đất, lấp đất và nén chặt quanh bầu.\n"
                  "4. Tưới đẫm sau khi trồng và che bóng tạm thời cho cây con.",
        luu_y="- Chọn cây xanh tốt, không vàng lá, rễ không cong queo.\n- Không để đọng nước trong hố trồng.\n"
              "- Vận chuyển nhẹ tay, tránh vỡ bầu."),
    "Hom tiêu Vĩnh Linh": dict(
        chi_tiet="- **Giống:** hồ tiêu Vĩnh Linh\n- **Hom:** ươm sẵn trong bầu, 5–7 đốt, đã ra rễ\n"
                 "- **Đơn vị:** 1 bầu\n- **Ưu điểm:** sinh trưởng khỏe, chùm dài.",
        huong_dan="1. Đào hố khoảng **50 × 50 × 50 cm** cạnh trụ, bón lót phân hữu cơ.\n"
                  "2. Rạch túi bầu, đặt bầu **nghiêng khoảng 45° hướng vào trụ**, cách trụ 15–20 cm.\n"
                  "3. Lấp đất, nén nhẹ, tưới ẩm và che nắng cho hom trong thời gian đầu.\n"
                  "4. Khi dây tiêu lớn, buộc dây vào trụ để dây bám.",
        luu_y="- Chọn hom sạch bệnh, lá xanh, không thối gốc.\n- Vườn phải **thoát nước tốt** để tránh bệnh chết nhanh.\n"
              "- Giữ ẩm đều nhưng không tưới quá nhiều."),
    "Bình phun điện 16 lít": dict(
        chi_tiet="- **Dung tích:** 16 lít\n- **Pin:** 12V – 8Ah, sạc lại được\n- **Thời gian phun:** khoảng 3–4 giờ mỗi lần sạc\n"
                 "- **Đi kèm:** dây đeo, cần phun, đầu béc phun có thể chỉnh tia",
        huong_dan="1. **Sạc đầy pin** trước lần dùng đầu tiên (khoảng 6–8 giờ).\n"
                  "2. Lọc dung dịch thuốc qua lưới lọc khi đổ vào bình, đậy chặt nắp.\n"
                  "3. Đeo bình lên vai, bật công tắc, xoay núm để chỉnh tia phun.\n"
                  "4. Phun xong: đổ hết thuốc thừa đúng nơi quy định, cho nước sạch vào phun vài phút để súc sạch vòi.",
        luu_y="- Không nhúng bình hoặc pin xuống nước.\n- Không để pin cạn kiệt lâu ngày; sạc lại sau mỗi lần dùng.\n"
              "- Đeo đồ bảo hộ khi phun thuốc bảo vệ thực vật."),
    "Kéo cắt cành": dict(
        chi_tiet="- **Lưỡi:** thép cứng, sắc bén\n- **Cắt được:** cành đường kính đến khoảng 2 cm\n"
                 "- **Tay cầm:** bọc nhựa chống trượt, có lò xo bật lại và khoá an toàn",
        huong_dan="1. Mở khoá an toàn, đặt lưỡi kéo sát phía trên mắt cành.\n2. Cắt **dứt khoát, vết cắt xiên** để nước mưa không đọng.\n"
                  "3. Khi cắt cây bị bệnh, lau lưỡi kéo bằng cồn trước khi sang cây khác.\n"
                  "4. Dùng xong lau sạch, để khô và tra một ít dầu vào chốt.",
        luu_y="- Luôn khoá lưỡi kéo khi cất.\n- Để xa tầm tay trẻ em.\n- Không dùng kéo để cắt dây kẽm, vật cứng."),
}
