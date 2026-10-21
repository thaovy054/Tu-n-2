import sys
import pandas as pd

COT_BAT_BUOC = ['trip_id', 'route_id', 'distance_km', 'actual_travel_time',
                'departure_time_full', 'time_slot', 'is_simulated', 'data_source']
DANH_MUC_DATA_SOURCE = {'osrm_api', 'openstreetmap', 'simulated', 'manual'}


def kiem_tra(file_path):
    df = pd.read_csv(file_path)
    loi = []

    # 1. Kiem tra cot bat buoc
    thieu = [c for c in COT_BAT_BUOC if c not in df.columns]
    if thieu:
        loi.append(f"Thieu cot: {thieu}")

    # 2. Kiem tra gia tri is_simulated chi la 0/1
    if 'is_simulated' in df.columns:
        gia_tri_la = set(df['is_simulated'].dropna().unique())
        if not gia_tri_la.issubset({0, 1}):
            loi.append(f"is_simulated co gia tri la: {gia_tri_la - {0, 1}}")

    # 3. Kiem tra data_source thuoc danh muc chuan
    if 'data_source' in df.columns:
        gia_tri_la = set(df['data_source'].dropna().unique())
        if not gia_tri_la.issubset(DANH_MUC_DATA_SOURCE):
            loi.append(f"data_source co gia tri la: {gia_tri_la - DANH_MUC_DATA_SOURCE}")

    # 4. Kiem tra kieu so va mien gia tri hop ly
    for cot in ['distance_km', 'actual_travel_time']:
        if cot in df.columns:
            if not pd.api.types.is_numeric_dtype(df[cot]):
                loi.append(f"{cot} khong phai kieu so")
            elif (df[cot] <= 0).any():
                loi.append(f"{cot} co gia tri <= 0")

    # 5. Kiem tra toa do (neu co)
    for cot in ['origin_lat', 'origin_lon', 'dest_lat', 'dest_lon']:
        if cot in df.columns and df[cot].notna().any():
            if cot.endswith('lat') and not df[cot].dropna().between(8, 13).all():
                loi.append(f"{cot} nam ngoai mien Viet Nam")
            if cot.endswith('lon') and not df[cot].dropna().between(100, 110).all():
                loi.append(f"{cot} nam ngoai mien Viet Nam")

    # 6. Kiem tra trip_id trung lap
    if 'trip_id' in df.columns and df['trip_id'].duplicated().any():
        loi.append("trip_id bi trung lap")

    if loi:
        print("[LOI] CSV khong hop le:")
        for l in loi:
            print("  -", l)
        sys.exit(1)
    print(f"[OK] CSV hop le: {len(df)} chuyen, {df['route_id'].nunique()} tuyen, "
          f"is_simulated={sorted(df['is_simulated'].unique())}, "
          f"data_source={sorted(df['data_source'].unique())}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "trips_ml_v1.csv"
    kiem_tra(path)
