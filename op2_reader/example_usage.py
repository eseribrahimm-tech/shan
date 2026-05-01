"""
Op2 Handler Kullanım Örneği

Bu script op2_handler.py'ı doğrudan Python'da nasıl kullanacağını gösterir.
GUI olmadan op2 dosyasını parse etmek için faydalı.
"""

from op2_handler import Op2Handler


def main():
    # Op2 dosya yolunu belirt
    op2_file = "your_file.op2"  # Buraya kendi op2 dosya yolunu gir

    try:
        # Op2 dosyasını yükle
        print("Dosya yükleniyor...")
        handler = Op2Handler(op2_file)
        print("✓ Dosya başarıyla yüklendi\n")

        # Tüm loadcase'leri göster
        loadcases = handler.get_loadcases()
        print(f"Toplam Loadcase: {len(loadcases)}")
        for subcase_id, description in loadcases.items():
            print(f"  - {description} (ID: {subcase_id})")

        # İlk loadcase'i al
        first_subcase = list(loadcases.keys())[0]
        print(f"\nSeçilen Loadcase: {first_subcase}")

        # O loadcase'de bulunan result type'larını göster
        result_types = handler.get_result_types(first_subcase)
        print(f"Mevcut Result Type'lar: {result_types}")

        # Node sonuçlarını getir (ilk node)
        if result_types:
            node_ids = handler.get_all_node_ids()
            if node_ids:
                first_node = node_ids[0]
                print(f"\nNode {first_node} Deplasman Sonuçları:")

                # Displacement sonuçlarını al
                if 'displacement' in result_types:
                    results = handler.get_node_results(
                        first_subcase, first_node, 'displacement'
                    )
                    for key, value in results.items():
                        print(f"  {key}: {value}")

        # Element sonuçlarını getir
        element_ids = handler.get_all_element_ids()
        if element_ids and 'stress' in result_types:
            first_element = element_ids[0]
            print(f"\nElement {first_element} Gerilim Sonuçları:")
            results = handler.get_element_results(
                first_subcase, first_element, 'stress'
            )
            for key, value in results.items():
                print(f"  {key}: {value}")

        print("\n✓ Örnek tamamlandı")

    except Exception as e:
        print(f"✗ Hata: {e}")


if __name__ == "__main__":
    main()
