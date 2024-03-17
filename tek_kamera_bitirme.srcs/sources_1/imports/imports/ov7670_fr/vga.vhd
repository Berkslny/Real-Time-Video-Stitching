
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;



entity VGA is
    Port ( CLK25 : in  STD_LOGIC;						-- 25 MHz giri? saati					
			  clkout : out  STD_LOGIC;					-- ADV7123 ve TFT ekran?na ç?k?? saati
           rez_160x120 : IN std_logic;
           rez_320x240 : IN std_logic;
           Hsync,Vsync : out  STD_LOGIC;				-- VGA ekran? için iki senkronizasyon sinyali
			  Nblank : out  STD_LOGIC;					-- ADV7123 D/A dönü?türücüsünün kontrol sinyali
           activeArea : out  STD_LOGIC;
			  Nsync : out  STD_LOGIC);	                -- TFT ekran?n?n senkronizasyon ve kontrol sinyalleri
end VGA;

architecture Behavioral of VGA is
signal Hcnt:STD_LOGIC_VECTOR(9 downto 0):="0000000000";		-- Sütun say?m? için
signal Vcnt:STD_LOGIC_VECTOR(9 downto 0):="1000001000";		-- Sat?r say?m? için
signal video:STD_LOGIC;
constant HM: integer :=799;	-- Maksimum göz önünde bulundurulan boyut 800 (yatay)
constant HD: integer :=640;	-- Ekran boyutu (yatay)
constant HF: integer :=16;		-- ön düzlük
constant HB: integer :=48;		-- arka düzlük
constant HR: integer :=96;		-- sync time
constant VM: integer :=524;	-- Maksimum göz önünde bulundurulan boyut 525 (dikey)
constant VD: integer :=480;	-- Ekran boyutu (dikey)
constant VF: integer :=10;		--ön düzlük
constant VB: integer :=33;		--arka düzlük
constant VR: integer :=2;		--retrace

begin

-- bir sayac?n 0'dan 799'a kadar ba?lat?lmas? (sat?r ba??na 800 piksel):
-- her saat darbesinde, sütun sayac? art?r?l?r
-- yani 0'dan 799'a kadar art?r?l?r
	process(CLK25)
		begin
			if (CLK25'event and CLK25='1') then
				if (Hcnt = HM) then
					Hcnt <= "0000000000";
               if (Vcnt= VM) then
                  Vcnt <= "0000000000";
                  activeArea <= '1';
               else
                  if rez_160x120 = '1' then
                     if vCnt < 120-1 then
                        activeArea <= '1';
                     end if;
                  elsif rez_320x240 = '1' then
                     if vCnt < 240-1 then
                        activeArea <= '1';
                     end if;
                  else
                     if vCnt < 480-1 then
                        activeArea <= '1';
                     end if;
                  end if;
                  Vcnt <= Vcnt+1;
               end if;
				else
               if rez_160x120 = '1' then
                  if hcnt = 160-1 then
                     activeArea <= '0';
                  end if;
               elsif rez_320x240 = '1' then
                  if hcnt = 320-1 then
                     activeArea <= '0';
                  end if;
               else
                  if hcnt = 640-1 then
                     activeArea <= '0';
                  end if;
               end if;
					Hcnt <= Hcnt + 1;
				end if;
			end if;
		end process;
----------------------------------------------------------------

-- Yatay senkronizasyon sinyali Hsync'in üretilmesi:
	process(CLK25)
		begin
			if (CLK25'event and CLK25='1') then
				if (Hcnt >= (HD+HF) and Hcnt <= (HD+HF+HR-1)) then   --- Hcnt >= 656 and Hcnt <= 751
					Hsync <= '0';
				else
					Hsync <= '1';
				end if;
			end if;
		end process;
----------------------------------------------------------------

-- Dikey senkronizasyon sinyali Vsync'in üretilmesi:
	process(CLK25)
		begin
			if (CLK25'event and CLK25='1') then
				if (Vcnt >= (VD+VF) and Vcnt <= (VD+VF+VR-1)) then  ---Vcnt >= 490 and vcnt<= 491
					Vsync <= '0';
				else
					Vsync <= '1';
				end if;
			end if;
		end process;
----------------------------------------------------------------

-- ADV7123 dönü?türücüyü kontrol etmek için Nblank ve Nsync:
Nsync <= '1';
video <= '1' when (Hcnt < HD) and (Vcnt < VD)			-- Tam çözünürlü?ü kullanmak için 640 x 480
	      else '0';
Nblank <= video;
clkout <= CLK25;

		
end Behavioral;

