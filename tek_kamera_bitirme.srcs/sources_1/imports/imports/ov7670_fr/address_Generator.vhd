
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

entity Address_Generator is
    Port ( 	CLK25,enable : in  STD_LOGIC;								-- S?ras?yla 25 MHz saat ve etkinle?tirme sinyali
            rez_160x120  : IN std_logic;
            rez_320x240  : IN std_logic;
            vsync        : in  STD_LOGIC;
				address 		 : out STD_LOGIC_VECTOR (18 downto 0));	-- Üretilen adres
end Address_Generator;

architecture Behavioral of Address_Generator is
   signal val: STD_LOGIC_VECTOR(address'range):= (others => '0');		-- Ara sinyal
begin
	address <= val;														-- Üretilen adres

	process(CLK25)
		begin
         if rising_edge(CLK25) then
            if (enable='1') then										-- enable = 0 ise adres üretimini durdururuz
               if rez_160x120 = '1' then
                  if (val < 160*120) then								-- E?er bellek alan? tamamen taran?rsa			
                     val <= val + 1 ;
                  end if;
               elsif rez_320x240 = '1' then
                  if (val < 320*240) then								-- E?er bellek alan? tamamen taran?rsa			
                     val <= val + 1 ;
                  end if;
               else
                  if (val < 640*480) then								-- E?er bellek alan? tamamen taran?rsa				
                     val <= val + 1 ;
                  end if;
               end if;
				end if;
            if vsync = '0' then 
               val <= (others => '0');
            end if;
			end if;	
		end process;
end Behavioral;

