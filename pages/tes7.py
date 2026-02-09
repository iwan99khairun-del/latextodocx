# ==========================================
            # 2. LOGIKA SURFACE CHART (DIPERBAIKI + ANTI CRASH)
            # ==========================================
            elif chart_type == "🏔️ Surface Chart (3D/Contour)":
                
                # Pilihan Gaya Surface
                surf_style = st.selectbox(
                    "Gaya Tampilan (Style)", 
                    ["🌈 Filled Surface (Isi)", "🕸️ Wireframe (Jaring)", "🗺️ Contour (Peta 2D)"]
                )
                
                c_x, c_y, c_z = st.columns(3)
                with c_x: x_axis = st.selectbox("Sumbu X", columns, key="sx")
                with c_y: y_axis = st.selectbox("Sumbu Y", columns, key="sy")
                with c_z: z_axis = st.selectbox("Sumbu Z (Nilai)", columns, key="sz")
                
                cmap_choice = st.selectbox("Warna", ["viridis", "plasma", "coolwarm", "terrain", "ocean"])

                if x_axis and y_axis and z_axis:
                    # 1. Cek apakah kolom X dan Y sama persis (Penyebab utama error)
                    if x_axis == y_axis:
                        st.warning("⚠️ Perhatian: Sumbu X dan Sumbu Y tidak boleh sama. Grafik 3D butuh dua sisi yang berbeda (Panjang & Lebar) agar bisa membentuk permukaan.")
                    else:
                        # Pastikan Numeric
                        df[x_axis] = pd.to_numeric(df[x_axis], errors='coerce')
                        df[y_axis] = pd.to_numeric(df[y_axis], errors='coerce')
                        df[z_axis] = pd.to_numeric(df[z_axis], errors='coerce')
                        df_surf = df.dropna(subset=[x_axis, y_axis, z_axis])

                        # 2. Pasang Try-Except (Pengaman Error Qhull)
                        try:
                            if surf_style == "🗺️ Contour (Peta 2D)":
                                # Plot 2D (Tricontourf)
                                ax = fig.add_subplot(111)
                                cntr = ax.tricontourf(df_surf[x_axis], df_surf[y_axis], df_surf[z_axis], levels=14, cmap=cmap_choice)
                                fig.colorbar(cntr, ax=ax, label=z_axis)
                                ax.set_title(f"Contour Plot: {z_axis}")
                            
                            elif surf_style == "🕸️ Wireframe (Jaring)":
                                # Plot 3D (Trisurf tapi transparan + garis tepi)
                                ax = fig.add_subplot(111, projection='3d')
                                ax.plot_trisurf(
                                    df_surf[x_axis], df_surf[y_axis], df_surf[z_axis], 
                                    color=(1,1,1,0), edgecolor='black', linewidth=0.5
                                )
                                ax.set_title(f"Wireframe Plot: {z_axis}")
                                
                            else: 
                                # Plot 3D (Filled) - Default
                                ax = fig.add_subplot(111, projection='3d')
                                surf = ax.plot_trisurf(
                                    df_surf[x_axis], df_surf[y_axis], df_surf[z_axis], 
                                    cmap=cmap_choice, edgecolor='none', alpha=0.9
                                )
                                fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label=z_axis)
                                ax.set_title(f"3D Surface: {z_axis}")

                            if surf_style != "🗺️ Contour (Peta 2D)":
                                ax.set_zlabel(z_axis)
                            
                            ax.set_xlabel(x_axis)
                            ax.set_ylabel(y_axis)

                        except Exception as e:
                            # Jika data membentuk garis lurus, kode ini akan jalan
                            st.error("⛔ Tidak bisa membuat Surface.")
                            st.markdown(f"""
                            **Penyebab:** Data X dan Y Anda membentuk garis lurus (segaris), sehingga tidak bisa ditarik selimut (surface) di atasnya.
                            
                            **Solusi:**
                            1. Pastikan Sumbu X dan Y adalah variabel yang **berbeda** dan tidak saling terkait sempurna (misal: jangan pakai data X=1,2,3 dan Y=2,4,6).
                            2. Coba ganti kombinasi kolom X atau Y nya.
                            
                            *Detail Error Komputer: {e}*
                            """)
