def get_float(prompt):
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                print("输入不能为空，请输入数字！")
                continue
            return float(user_input)
        except ValueError:
            print("输入格式错误，请输入数字（支持小数，例如 12.5）")


def in_range(value, min_value, max_value):
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def calculate_shipping(length, width, height, weight, price):
    volume_weight = length * width * height / 12000
    chargeable_weight = max(weight, volume_weight)
    dimension_sum = length + width + height
    max_side = max(length, width, height)

    # 全局物流限制
    if max_side > 150:
        return volume_weight, chargeable_weight, "超出尺寸：最长边不能超过150cm"
    if dimension_sum > 310:
        return volume_weight, chargeable_weight, "超出尺寸：长宽高总和不能超过310cm"
    if weight > 30:
        return volume_weight, chargeable_weight, "超出重量：实际重量不能超过30kg"
    if volume_weight > 30:
        return volume_weight, chargeable_weight, "超出重量：体积重量不能超过30kg"

    services = [
        {
            "name": "Extra small",
            "weight_min": 0,
            "weight_max": 0.5,
            "price_min": 0,
            "price_max": 1500,
            "sum_max": 90,
            "side_max": 60,
            "use_volume": False,
            "formula": lambda w: 3.12 + 0.0364 * w * 1000,
        },
        {
            "name": "Budget",
            "weight_min": 0.5,
            "weight_max": 25,
            "price_min": 0,
            "price_max": 1500,
            "sum_max": 150,
            "side_max": 60,
            "use_volume": False,
            "formula": lambda w: 23.92 + 0.026 * w * 1000,
        },
        {
            "name": "Small",
            "weight_min": 0,
            "weight_max": 2,
            "price_min": 1501,
            "price_max": 7000,
            "sum_max": 150,
            "side_max": 60,
            "use_volume": False,
            "formula": lambda w: 16.64 + 0.0364 * w * 1000,
        },
        {
            "name": "Premium small",
            "weight_min": 0,
            "weight_max": 5,
            "price_min": 7001,
            "price_max": 250000,
            "sum_max": 250,
            "side_max": 150,
            "use_volume": False,
            "formula": lambda w: 22.88 + 0.0364 * w * 1000,
        },
        {
            "name": "Big",
            "weight_min": 2.001,
            "weight_max": 30,
            "price_min": 1501,
            "price_max": 7000,
            "sum_max": 310,
            "side_max": 150,
            "use_volume": True,
            "formula": lambda w: 37.74 + 0.026 * w * 1000,
        },
        {
            "name": "Premium big",
            "weight_min": 5.001,
            "weight_max": 30,
            "price_min": 7001,
            "price_max": 250000,
            "sum_max": 310,
            "side_max": 150,
            "use_volume": True,
            "formula": lambda w: 64.48 + 0.02392 * w * 1000,
        },
    ]

    results = []
    for service in services:
        if not in_range(weight, service["weight_min"], service["weight_max"]):
            continue
        if not in_range(price, service["price_min"], service["price_max"]):
            continue
        if service["sum_max"] is not None and dimension_sum > service["sum_max"]:
            continue
        if service["side_max"] is not None and max_side > service["side_max"]:
            continue
        service_weight = max(weight, volume_weight) if service["use_volume"] else weight
        cost = service["formula"](service_weight)
        results.append((service["name"], cost))

    return volume_weight, chargeable_weight, results


def calculate_pricing(CB, YF_rmb, YSJ, PTFL, HL=11.2, manual_profit_rate=None):
    """
    全部核算单位：卢布
    CB: 产品成本(人民币)
    YF_rmb: 物流运费(人民币)
    YSJ: 预售价(卢布)
    PTFL: 平台费率
    HL: 汇率 1人民币 = HL 卢布
    manual_profit_rate: 可选手动利润率，单位为小数（例如 0.2 代表 20%）
    """
    # 成本转为卢布
    CB_rub = CB * HL
    # 运费人民币 → 乘汇率转为卢布
    YF_rub = YF_rmb * HL
    # 品牌推广费：预售价 1%
    TG = YSJ * 0.00
    # 平台费用
    PTF = YSJ * PTFL
    # 评价费 固定250卢布
    JP = 0
    # 利润：默认取 运费卢布*12% 、预售价*20% 的较大值；
    # 可通过 manual_profit_rate 手动指定利润率（小数），此时 利润 = 进价(卢布) * 手动利润率
    if manual_profit_rate is not None:
        # 强制按利润率处理：利润 = 成本(卢布) * 利润率
        LR = CB_rub * float(manual_profit_rate)
    else:
        LR = max(YF_rub * 0.12, YSJ * 0.2)
    # 最终核算售价(卢布)
    SJ = CB_rub + TG + PTF + JP + YF_rub + LR
    # 差值 = 预售价 - 核算售价
    diff = YSJ - SJ
    # 合规判断：0 ≤ 差值 ≤ 4
    is_valid = 0 <= diff <= 4

    return {
        "CB_rub": CB_rub,
        "YF_rub": YF_rub,
        "TG": TG,
        "PTF": PTF,
        "JP": JP,
        "LR": LR,
        "SJ": SJ,
        "diff": diff,
        "is_valid": is_valid
    }


# 封装物流计算函数，方便重复调用
def calc_shipping_once(length, width, height, weight, price):
    vol_w, charge_w, res = calculate_shipping(length, width, height, weight, price)
    return vol_w, charge_w, res


def main():
    print("===== 物流+定价综合计算器 =====")
    print("【第一步 录入固定尺寸/重量信息】")
    # 尺寸重量只输入一次，不会变动
    length = get_float("长度（cm）：")
    width = get_float("宽度（cm）：")
    height = get_float("高度（cm）：")
    weight = get_float("重量（kg）：")

    # 初始预售价
    price_input = get_float("商品初始预售价（卢布）：")

    # 第二步 录入定价固定信息
    print("\n【第二步 录入成本/费率/汇率信息】")
    cost_rmb = get_float("产品成本（人民币元）：")
    platform_rate = get_float("平台费率（如0.05代表5%）：")
    exchange = get_float("汇率(1元=?卢布，默认11.2)：")
    if exchange <= 0:
        exchange = 11.2

    # ========== 循环：重新输入预售价 → 重新算物流 → 重新算定价 ==========
    # 手动利润率模式：一旦选择手动输入(y)，后续循环不再询问，直接使用该值
    manual_mode = False
    manual_profit_rate = None
    while True:
        # 每次都用最新预售价 重新计算物流
        vol_w, charge_w, res = calc_shipping_once(length, width, height, weight, price_input)

        print(f"\n----- 最新物流计算结果 -----")
        print(f"体积重量：{vol_w:.3f} kg")
        print(f"计费重量：{charge_w:.3f} kg")

        # 物流异常拦截
        if isinstance(res, str):
            print(f"❌ 物流异常：{res}")
            price_input = get_float("请重新输入商品预售价（卢布）：")
            continue
        if not res:
            print("❌ 无匹配物流服务，请检查参数")
            price_input = get_float("请重新输入商品预售价（卢布）：")
            continue

        # 获取最新物流运费（人民币）
        best_service = min(res, key=lambda x: x[1])
        ship_name, ship_cost_rmb = best_service
        print(f"✅ 优选物流：{ship_name}")
        print(f"✅ 最新物流运费（人民币）：{ship_cost_rmb:.2f}")

        # 询问是否手动设置利润率（仅首次选择后生效）
        if not manual_mode:
            use_manual = input("是否手动设置利润率？(y/N)：").strip().lower()
            if use_manual == 'y':
                manual_profit_rate = get_float("请输入利润率（例如0.2代表20%）：")
            manual_mode = True

        # 使用最新预售价 + 最新运费 计算定价
        price_data = calculate_pricing(cost_rmb, ship_cost_rmb, price_input, platform_rate, exchange, manual_profit_rate=manual_profit_rate)

        print("\n----- 最新定价明细（单位：卢布）-----")
        print(f"产品成本(转卢布)：{price_data['CB_rub']:.2f}")
        print(f"物流运费(转卢布)：{price_data['YF_rub']:.2f}")
        print(f"品牌推广费：{price_data['TG']:.2f}")
        print(f"平台费用：{price_data['PTF']:.2f}")
        print(f"评价服务费：{price_data['JP']:.2f}")
        print(f"利润：{price_data['LR']:.2f}")
        print(f"核算综合售价：{price_data['SJ']:.2f}")
        print(f"当前预售价：{price_input:.2f}")
        print(f"预售价 - 核算售价 = {price_data['diff']:.2f}")

        if price_data["is_valid"]:
            print("\n✅ 差值在 0~4 区间内，定价合规！")
            # 将最终卢布定价转换成人民币（人民币 = 卢布 / 汇率）
            final_price_rmb = price_input / exchange if exchange else None
            if final_price_rmb is not None:
                print(f"最终定价折合人民币：{final_price_rmb:.2f} 元")
                print(f"上品价：{final_price_rmb * 2.5:.2f} 元")
            break
        else:
            print("\n❌ 差值不在 0~4 区间内，请重新填写预售价！")
            price_input = get_float("请重新输入商品预售价（卢布）：")

    print("\n🎉 最终定价已确认，可以使用！")

    # 等待按下 ESC 键后退出（跨平台）
    def wait_for_esc():
        import sys
        try:
            # Windows
            import msvcrt
            print('\n请按 ESC 键退出...')
            while True:
                ch = msvcrt.getch()
                if ch == b'\x1b':
                    break
        except Exception:
            # POSIX
            import tty, termios
            print('\n请按 ESC 键退出...')
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while True:
                    ch = sys.stdin.read(1)
                    if ch == '\x1b':
                        break
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)

    wait_for_esc()