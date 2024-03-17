
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;


entity RGB is
    Port ( Din 	: in	STD_LOGIC_VECTOR (11 downto 0);			-- 8 bit üzerinde piksellerin gri seviyesi
			  Nblank : in	STD_LOGIC;							-- Sinyal, görüntüleme alan?n? görüntüleme alan? d???ndakilerini gösterir
																-- Üç renkte s?f?r al?r
           R,G,B 	: out	STD_LOGIC_VECTOR (7 downto 0));		-- Üç renk 10 bit üzerinde
end RGB;

architecture Behavioral of RGB is

begin
		R <= Din(11 downto 8) & Din(11 downto 8) when Nblank='1' else "00000000";
		G <= Din(7 downto 4)  & Din(7 downto 4)  when Nblank='1' else "00000000";
		B <= Din(3 downto 0)  & Din(3 downto 0)  when Nblank='1' else "00000000";

end Behavioral;

